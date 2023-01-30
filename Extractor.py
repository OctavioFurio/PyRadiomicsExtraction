
# V2.2 - Extração radiomica de imagens .tif
# 30.01.23

import os
import sys
import six
import gc
import numpy as np
import SimpleITK as sitk
import radiomics
from radiomics import featureextractor



def main():
    Diretorio, Parametros, Log = sys.argv[1], sys.argv[2], sys.argv[3]
    print("\n\tDiretorio selecionado: %s\n\tParametros: %s\n\tResultados armazenados em: %s" % (Diretorio, Parametros, Log))
    
    count = 0
    for path in os.scandir(Diretorio):
        if path.is_file():
            count += 1

    print('\n\tArquivos encontrados no diretorio: ', count)
    print("\n\tExtraindo caracteristicas...\n")

    radiomics.setVerbosity(30)

    FileSave(Diretorio, Parametros, Log, count)

    print("\n\tConteudo do arquivo .arff resultante:\n")

    print(open(Log, "r").read())



#   Escrita no arquivo .arff a ser gerado.
#   Formatação .arff padrão:

    #   @Relation Nome_da_relação
    #   
    #   @Attribute A Numeric
    #   @Attribute B Numeric
    #   ...
    #
    #   @Data
    #   1.212,5.634,... #imagem 1
    #   2.323,3.237,... #imagem 2
    #   ...

def FileSave(pathToDir, params, logName, totalFiles):
    arquivo = open(logName, "w")
    arquivo.write("% Caracteristicas extraidas do diretorio /" + pathToDir + "\n\n@RELATION Caracteristicas_Radiomicas\n\n")

    index = 1
    for _, _, files in os.walk(pathToDir):
        for file in sorted(files):
            pathToFile = pathToDir + "/" + file

            percentage = (int)(100 * (index-1) /(totalFiles))             

            result = runExtractor(pathToFile, params)

            if index != 1:
                arquivo.write("\n\n% " + file + "\n")
                dataWriter(arquivo, result)
                index += 1

            else: 
                i = 0
                for key, _ in six.iteritems(result):
                    if i < 37:  # 37 primeiros atributos são diagnósticos, e iguais em todas as imagens
                        i += 1
                        continue
                    arquivo.write("@ATTRIBUTE " + key + "\tNUMERIC\n")
                arquivo.write("@ATTRIBUTE class\t{sim,nao}\n")  # A classe ("sim" ou "não") é adicionada manualmente em cada imagem após a execução 
                arquivo.write("\n@DATA")
                arquivo.write("\n\n% " + file + "\n")
                dataWriter(arquivo, result)
                index += 1
                
                del result
                gc.collect

            print("\t%3d %% concluido -> Extraindo caracteristicas de" % (percentage), file)

    print("\t100 % concluido -> Imagens analisadas com sucesso.")



def addDimension(image):
    imagem = sitk.ReadImage(image)
    layers = 3

    eixo_x, eixo_z = imagem.GetWidth(), imagem.GetHeight()
    volume = sitk.Image([eixo_x, layers, eixo_z], imagem.GetPixelID())

    for i in range(layers):
        imagem = sitk.PermuteAxes(sitk.JoinSeries([sitk.ReadImage(image)]),[0,2,1])
        volume = sitk.Paste(volume, imagem, [eixo_x, 1, eixo_z], [0,0,0], [0,i,0])
    
    return volume



# Execução do extrator
def runExtractor(pathToImage, paramsFileName):
    volume = addDimension(pathToImage)

    params = os.path.join('./', paramsFileName)
    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(params, additionalInfo=True)
    
    return extractor.execute(volume, volume)
    


# Registro dos dados de cada nova imagem no arquivo .arff resultante.
def dataWriter(arquivo, result):
    i = 0
    for key, val in six.iteritems(result):
        if i < 37:  # 37 primeiros atributos são diagnósticos, e iguais em todas as imagens
            i += 1
            continue
        arquivo.write(str(val) + ',')



if __name__ == "__main__":
    main()
