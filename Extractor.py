
# V2.4 - Extração radiomica de imagens .tif
# 31.01.23

import os
import sys
import six
import gc
import numpy as np
import SimpleITK as sitk
import radiomics
from radiomics import featureextractor

def main():
    Diretorio, Parametros, Log = sys.argv[1], sys.argv[2], sys.argv[1] + "_Features.csv"
    print("\n\tDiretorio selecionado: %s\n\tParametros: %s\n\tResultados armazenados em: %s" % (Diretorio, Parametros, Log))
    
    count = 0
    for path in os.scandir(Diretorio):
        if path.is_file():
            count += 1

    print('\n\tArquivos encontrados no diretorio: ', count)
    print("\n\tExtraindo caracteristicas...\n")

    # Um menor valor trará mais informações durante a execução
    radiomics.setVerbosity(30)

    FileSave(Diretorio, Parametros, Log, count)

    print("\n\tArquivo .csv resultante: " + Log)



#   Escrita no arquivo .csv gerado
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
                arquivo.write("Nome,")
                for key, _ in six.iteritems(result):
                    if i < 37:  # 37 primeiros atributos são diagnósticos, e iguais em todas as imagens
                        i += 1
                        continue
                    arquivo.write(str(key)[9:] + ",")
                
                # A classe ("sim" ou "não") é adicionada manualmente em cada imagem após a execução
                arquivo.write("class\n")   
                dataWriter(arquivo, result, file)
                index += 1
                
                del result
                gc.collect

            print("\t%3d %% concluido -> Extraindo caracteristicas de" % (percentage), file)

    print("\t100 % concluido -> Imagens analisadas com sucesso.")



# Adiciona terceira dimensão às imagens e retorna um volume
def addDimension(image):        
    imagem = sitk.ReadImage(image)

    tileFilter = sitk.TileImageFilter()     # Utiliza-se essa função para unir as imagens em um novo volume
        
    tileFilter.SetLayout([1,1,0])           # Layout para unir as imagens no eixo Z, uma sob a outra, permitindo o uso de extratores GLCM
    tileFilter.SetDefaultPixelValue(128)
    
    tiff = sitk.ReadImage(image)
    
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
    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(params, additionalInfo=True)

    return extractor.execute(volume, volume)
    


# Registro dos dados de cada nova imagem no arquivo .csv resultante.
def dataWriter(arquivo, result, file):

    arquivo.write(str(file) + ",")

    i = 0
    for _, val in six.iteritems(result):
        if i < 37:  # 37 primeiros atributos são diagnósticos, e iguais em todas as imagens
            i += 1
            continue
        arquivo.write(str(val) + ',')
    arquivo.write("\n")



if __name__ == "__main__":
    main()
