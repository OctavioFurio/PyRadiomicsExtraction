
# V3.0 - Extração radiomica de imagens .tif
# 10.02.23

import os
import gc
import sys
import six
import radiomics
import numpy as np
import SimpleITK as sitk
from datetime import datetime
from datetime import timedelta
from radiomics import featureextractor
from timeit import default_timer as timer

def main():
    Diretorio, Parametros, Log = sys.argv[1], sys.argv[2], sys.argv[1] + "_Features.csv"

    global brilho, contraste

    if sys.argv[4: ]:
        brilho, contraste = float(sys.argv[3]), float(1.0 + (float(sys.argv[4])/-100.0))
    else:
        brilho, contraste = 0.0, 1.0

    print("\n\tDiretorio selecionado:\t%s\n\tParametros:\t\t%s\n\tArquivo .csv:\t\t%s" % (Diretorio, Parametros, Log))
    
    count = 0
    for path in os.scandir(Diretorio):
        if path.is_file():
            count += 1

    print('\n\tArquivos encontrados no diretorio: ', count)
    print("\n\tExtraindo caracteristicas...\n")

    # Um menor valor trará mais informações durante a execução
    radiomics.setVerbosity(30)
    
    Começo_da_execução = timer()

    FileSave(Diretorio, Parametros, Log, count)

    Fim_da_execução = timer()
    tempo_de_execução = timedelta(seconds=Fim_da_execução - Começo_da_execução)
    writeLogFile("Log_" + sys.argv[1] + ".txt", Diretorio, Parametros, tempo_de_execução)



# Pré-Processamento
def prepare(image):
    img_Contraste = sitk.AdaptiveHistogramEqualization(image, alpha=contraste, beta=1)

    # Contraste não-destrutivo
    histogram_match = sitk.HistogramMatchingImageFilter()
    histogram_match.SetThresholdAtMeanIntensity(True) 

    # Brilho não-destrutivo
    Shift_filter = sitk.ShiftScaleImageFilter()
    Shift_filter.SetShift(brilho)

    # Aplicar brilho e contraste
    im_matched = histogram_match.Execute(image, img_Contraste)

    del img_Contraste

    # Salvar imagens tratadas
    # save = Shift_filter.Execute(im_matched)
    # sitk.WriteImage(save, "LastImageSample.jpg")
    
    gc.collect
    return Shift_filter.Execute(im_matched)



# Escrita no arquivo .csv gerado
def FileSave(pathToDir, params, logName, totalFiles):
    
    arquivo = open(logName, "w")
    
    index = 1
    for _, _, files in os.walk(pathToDir):
        for file in sorted(files):
            pathToFile = pathToDir + "/" + file

            percentage = (int)(100 * (index-1) /(totalFiles))             

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



# Adiciona terceira dimensão às imagens e retorna um volume
def addDimension(image):        
    tileFilter = sitk.TileImageFilter()     # Utiliza-se essa função para unir as imagens em um novo volume
        
    tileFilter.SetLayout([1,1,0])           # Layout para unir as imagens no eixo Z, uma sob a outra, permitindo o uso de extratores GLCM
    tileFilter.SetDefaultPixelValue(128)
    
    tiff = sitk.ReadImage(image)
    tiff = prepare(tiff)
    
    im_vect = sitk.JoinSeries(tiff)
    volume = tileFilter.Execute(im_vect, im_vect, im_vect)  # "Empilham-se" 3 cópias da imagem para gerar um volume de altura 3
    
    # Caso necessário, este trecho realiza o corte da imagem em dadas coordenadas [x, y, z]
        # ResHorizontal, ResVertical = imagem.GetWidth(), imagem.GetHeight()
        # layers = 3
        # volume = volume[0:ResHorizontal, 0:ResVertical, 0:layers]

    # Salva o volume como .nrrd
        # sitk.WriteImage(volume, image + '.nrrd')

    return volume



# Execução do extrator
def runExtractor(pathToImage, paramsFileName):
    volume = addDimension(pathToImage)

    params = os.path.join('./', paramsFileName)

    stats = sitk.StatisticsImageFilter()
    stats.Execute(volume)

    label = int((stats.GetMinimum() + stats.GetMaximum()) / 2)

    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(params, label=label, additionalInfo=True)
    
    return extractor.execute(volume, volume)
    


# Registro dos dados de cada nova imagem no arquivo .csv resultante.
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
    diagnostics.write("\n\t- Brilho:\t" + str(brilho))
    diagnostics.write("\n\t- Contraste:\t" + str(100 * (1 - contraste)))
    diagnostics.write("\n\n\t> Duração:\t" + str(time))
    diagnostics.write("\n\nArquivo .csv resultante salvo em /" + dir + "_Features.csv")



if __name__ == "__main__":
    main()
