
# ----------------------------------------------------------- #
# Automação da biblioteca PyRadiomics para extração de  
# características radiômicas de imagens bidimensionais.
#
#                       v3.2 - 21.02.23
#
# Released under BSD 3-Clause "New" or "Revised" License
# ----------------------------------------------------------- #

import os
import gc
import sys
import six
import cv2
import radiomics
import numpy as np
import SimpleITK as sitk
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer



def main():
    global brilho, contraste, stdLabel
    Diretorio, Parametros, Log = sys.argv[1], sys.argv[2], sys.argv[1] + "_Features.csv"

    # Valores padrão dos parâmetros adicionais
    brilho      = int(sys.argv[3]) / 2.0   if sys.argv[4:] else 0.0
    contraste   = int(sys.argv[4]) / 2.0   if sys.argv[4:] else 0.0
    stdLabel    = int(sys.argv[5])         if sys.argv[5:] else 100
    
    print("\n\tDiretorio selecionado:\t%s\n\tParametros:\t\t%s\n\tArquivo .csv:\t\t%s" % (Diretorio, Parametros, Log))
    
    count = 0
    for path in os.scandir(Diretorio):
        if path.is_file():
            count += 1

    print('\n\tArquivos encontrados no diretorio: ', count)
    print("\n\tExtraindo caracteristicas...")

    # Um menor valor trará mais informações sobre erros e processos durante a execução
    radiomics.setVerbosity(15)
    
    Começo_da_execução = timer()

    extractionAutomation(Diretorio, Parametros, Log, count)

    Fim_da_execução = timer()
    tempo_de_execução = timedelta(seconds = Fim_da_execução - Começo_da_execução)

    print("\n\n\t\t--> Finalizando...\n")

    writeLogFile("Log_" + sys.argv[1] + ".txt", Diretorio, Parametros, tempo_de_execução)



########## Definição das funções ##########

# Escrita no arquivo .csv gerado
def extractionAutomation(pathToDir, params, logName, totalFiles):
    arquivo = open(logName, "w")

    index = 1
    for _, _, files in os.walk(pathToDir):
        for file in sorted(files): 
            print("\n\t%s/%s - Processando" % (index, totalFiles), file)

            pathToFile = pathToDir + "/" + file
            result = runExtractor(pathToFile, params)
            print("\n\t- Extrator finalizou seus processos\n\t\t> %s teve suas caracteristicas extraidas" %(file))

            if index != 1:
                dataWriter(arquivo, result, file)
                index += 1

            else: 
                i = 0
                arquivo.write("Nome,class")
                for key, _ in six.iteritems(result):
                    # 37 primeiros atributos são diagnósticos, e iguais em todas as imagens
                    if i < 37:  
                        i += 1
                        continue
                    arquivo.write("," + str(key)[9:])
                
                # A classe ("sim" ou "não") é adicionada manualmente em cada imagem após a execução
                arquivo.write("\n")   
                dataWriter(arquivo, result, file)
                index += 1
                
                del result
                gc.collect



# Pré-processamento, Volumetrização e Execução do extrator
def runExtractor(pathToImage, paramsFileName):
    # Funções para volumetrização
    tileFilter = sitk.TileImageFilter()     
    tileFilter.SetLayout([1,1,0])           
    tileFilter.SetDefaultPixelValue(128)

    # Leitura da imagem
    imagemOriginal = cv2.imread(pathToImage)

    # Pré-processamento
    if brilho != 0:
        if brilho > 0:
            BrilhoEfetivo = brilho
            maxValues = 255
        else:
            BrilhoEfetivo = 0
            maxValues = 255 + brilho
        imagemProcessada = cv2.addWeighted(imagemOriginal, (maxValues - BrilhoEfetivo) / 255, imagemOriginal, 0, BrilhoEfetivo)

    else:
        imagemProcessada = imagemOriginal
  
    if contraste != 0:
        Alpha = float(131 * (contraste + 127)) / (127 * (131 - contraste))
        Gamma = 127 * (1 - Alpha)
  
        imagemProcessada = cv2.addWeighted(imagemProcessada, Alpha, imagemProcessada, 0, Gamma)

    # Parâmetros e Label para extração
    params = os.path.join('./', paramsFileName)
    extractionLabel = stdLabel

    # Label inserida não presente na imagem
    if not (np.array(imagemProcessada) == extractionLabel).any():
       print("\n\t*** [AVISO] Problemas com a label (", str(extractionLabel), "). Nova label:", str(extractionLabel - 1), "\n")
       extractionLabel -= 1

    # Resolução de overflow
    hsvImage = cv2.cvtColor(imagemProcessada, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsvImage)
    v[v >= 255] = 255
    v[v <= 0] = 0
    hsvImage = cv2.merge((h, s, v))
    imagemProcessada = cv2.cvtColor(cv2.cvtColor(hsvImage, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
    imagemProcessada = sitk.GetImageFromArray( np.array(imagemProcessada) )

    print("\t- Pre-processamento de", str(pathToImage), "concluido\n\t\t> Brilho:", brilho*2, "/ Contraste:", contraste*2)

    # Salva imagens pré-processadas, para facilitar testes
    # nome = str(pathToImage.split(".")[0].split("/")[1] + "(Brilho " + str(int(brilho * 2)) + " Contraste " + str(int(contraste * 2)) + ").tif")
    # sitk.WriteImage(imagemProcessada, nome)

    # Volumetrização da imagem pré-processada
    imagemProcessada = sitk.JoinSeries(imagemProcessada)
    ### "Empilham-se" 3 cópias da imagem para gerar um volume de altura 3
    volume = tileFilter.Execute(imagemProcessada, imagemProcessada, imagemProcessada)  
    
    # Salva os volumes gerados, para facilitar testes
    # nome = str(pathToImage.split(".")[0].split("/")[1] + "(Brilho " + str(int(brilho * 2)) + " Contraste " + str(int(contraste * 2)) + ").tif")
    # sitk.WriteImage(volume, nome + '.nrrd')

    # Extração das características
    print("\t- Extracao de", str(pathToImage), "iniciada [ label:",str(extractionLabel),"]\n\tSeguem dados adicionais:\n")
    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(params, label=extractionLabel, additionalInfo=True)
    return extractor.execute(volume, volume)
    


# Registro dos dados de cada nova imagem em uma nova linha do arquivo .csv resultante
def dataWriter(arquivo, result, file):
    arquivo.write(str(file) + ",")

    print("\t- Resultados salvos no .csv com sucesso")

    i = 0
    for _, val in six.iteritems(result):
        if i < 37:  # 37 primeiros atributos são diagnósticos, e iguais em todas as imagens
            i += 1
            continue
        arquivo.write(',' + str(val))
    arquivo.write("\n")

# Arquivo Log.txt com dados diagnósticos da extração
def writeLogFile(name, dir, params, time):
    diagnostics = open(name, "w")
    data = datetime.now()
    dataAtual = data.strftime("%d/%m/%Y %H:%M:%S")

    diagnostics.write("Arquivo gerado automaticamente em " + dataAtual + "\n\n")
    diagnostics.write("Dados da extração de Características Radiômicas do diretório /" + dir + "\n")

    diagnostics.write("\n\t- Parâmetros:\t" + params)
    diagnostics.write("\n\t- Brilho:\t" + str(2 * brilho))
    diagnostics.write("\n\t- contraste:\t" + str(2 * contraste))

    diagnostics.write("\n\n\t> Duração:\t" + str(time))
    diagnostics.write("\n\nArquivo .csv resultante salvo em /" + dir + "_Features.csv")



if __name__ == "__main__":
    main()
