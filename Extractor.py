
# V3.1 - Extração radiomica de imagens .tif
# 14.02.23

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

########## Definição das funções ##########

# Escrita no arquivo .csv gerado
def extractionAutomation(pathToDir, params, logName, totalFiles):
    arquivo = open(logName, "w")
    
    index = 1
    for _, _, files in os.walk(pathToDir):
        for file in sorted(files):
            percentage = (int)(100 * (index-1) /(totalFiles))             

            pathToFile = pathToDir + "/" + file
            result = runExtractor(pathToFile, params)

            if index != 1:
                dataWriter(arquivo, result, file)
                index += 1

            else: 
                i = 0
                arquivo.write("Nome,class")
                for key, _ in six.iteritems(result):
                    if i < 37:  # 37 primeiros atributos são diagnósticos, e iguais em todas as imagens
                        i += 1
                        continue
                    arquivo.write("," + str(key)[9:])
                
                # A classe ("sim" ou "não") é adicionada manualmente em cada imagem após a execução
                arquivo.write("\n")   
                dataWriter(arquivo, result, file)
                index += 1
                
                del result
                gc.collect

            print("\t%3d %% concluido -> Extraindo caracteristicas de" % (percentage), file)
    print("\t100 % concluido -> Imagens analisadas com sucesso.")

# Pré-processamento, Volumetrização e Execução do extrator
def runExtractor(pathToImage, paramsFileName):
    # Funções para volumetrização
    tileFilter = sitk.TileImageFilter()     # Utiliza-se essa função para unir as imagens em um novo volume
    tileFilter.SetLayout([1,1,0])           # Layout para unir as imagens no eixo Z, uma sob a outra, permitindo o uso de extratores GLCM
    tileFilter.SetDefaultPixelValue(128)

    # Leitura da imagem
    tiff = sitk.ReadImage(pathToImage)
    imagemOriginal = sitk.GetArrayFromImage(tiff)
  
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
        Alpha = float((128 + contraste)) / ((128 - contraste))
        Gamma = 128 * (1 - Alpha)
  
        imagemProcessada = cv2.addWeighted(imagemProcessada, Alpha, imagemProcessada, 0, Gamma)

    imagemProcessada = sitk.GetImageFromArray( np.array(imagemProcessada) )

    # Salva imagens pré-processadas, para facilitar testes
    nome = str(pathToImage.split(".")[0].split("/")[1] + "(Brilho " + str(int(brilho * 2)) + " Contraste " + str(int(contraste * 2)) + ").tif")
    sitk.WriteImage(imagemProcessada, nome)
    
    # Volumetrização da imagem pré-processada
    imagemProcessada = sitk.JoinSeries(imagemProcessada)
    volume = tileFilter.Execute(imagemProcessada, imagemProcessada, imagemProcessada)  # "Empilham-se" 3 cópias da imagem para gerar um volume de altura 3

    params = os.path.join('./', paramsFileName)

    # Labeling automatizado, baseado na média de níveis da imagem
    stats = sitk.StatisticsImageFilter()
    stats.Execute(volume)
    label = int(stats.GetMean() + 1)

    # Extração
    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(params, label=label, additionalInfo=True)
    return extractor.execute(volume, volume)
    
# Registro dos dados de cada nova imagem em uma nova linha do arquivo .csv resultante
def dataWriter(arquivo, result, file):
    arquivo.write(str(file) + ",")

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
    diagnostics.write("Dados da extração de Características Radiômicas do diretório /" + dir + "\n\n")
    diagnostics.write("\t- Parâmetros:\t" + params)
    diagnostics.write("\n\t- Brilho:\t" + str(2 * brilho))
    diagnostics.write("\n\t- contraste:\t" + str(2 * contraste))
    diagnostics.write("\n\n\t> Duração:\t" + str(time))
    diagnostics.write("\n\nArquivo .csv resultante salvo em /" + dir + "_Features.csv")



########## Main ##########

if __name__ == "__main__":
    global brilho, contraste
    Diretorio, Parametros, Log = sys.argv[1], sys.argv[2], sys.argv[1] + "_Features.csv"

    if sys.argv[4: ]:
        brilho, contraste = (float(sys.argv[3]) / 2) , (float(sys.argv[4]) / 2)
    else:
        brilho, contraste = 0.0, 0.0

    print("\n\tDiretorio selecionado:\t%s\n\tParametros:\t\t%s\n\tArquivo .csv:\t\t%s" % (Diretorio, Parametros, Log))
    
    count = 0
    for path in os.scandir(Diretorio):
        if path.is_file():
            count += 1

    print('\n\tArquivos encontrados no diretorio: ', count)
    print("\n\tExtraindo caracteristicas...\n")

    # Um menor valor trará mais informações sobre erros e processos durante a execução
    radiomics.setVerbosity(30)
    
    Começo_da_execução = timer()

    extractionAutomation(Diretorio, Parametros, Log, count)

    Fim_da_execução = timer()
    tempo_de_execução = timedelta(seconds = Fim_da_execução - Começo_da_execução)

    writeLogFile("Log_" + sys.argv[1] + ".txt", Diretorio, Parametros, tempo_de_execução)
