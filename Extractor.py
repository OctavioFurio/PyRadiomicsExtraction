dados = """
    -------------------------------------------------------- 
     Automação da biblioteca PyRadiomics para extração de  
     características radiômicas de imagens bidimensionais.
    
                        v4.4 - 08.06.23
    
     Released under BSD 3-Clause "New" or "Revised" License
    -------------------------------------------------------- 
"""

import os
import sys
import cv2
import radiomics
import six
import numpy as np
import pandas as pd
import SimpleITK as sitk

def main():
    global brilho, contraste, parametros, diretorio, logName
        
    diretorio, parametros, logName = sys.argv[1], sys.argv[2], sys.argv[1] + "_Features.csv"

    # Input de brilho & contraste
    # Se não inicializados, terão valor zero
    brilho      = int(sys.argv[3]) / 2.0   if sys.argv[4:] else 0.0
    contraste   = int(sys.argv[4]) / 2.0   if sys.argv[4:] else 0.0
    
    print(f"{dados}\n\n\tInicializando...")

    extrair(diretorio)


def extrair(imagens):
    arquivoCSVresultante = open(logName, "w")

    classesDasImagens = [
        # Labels das imagens, levando em conta que serão lidas
        # em ordem alfabética.
        #
        # 0 = Controle/Tecido adjacente
        # 1 = Câncer
    ]

    indiceDaImagem = 0
    for imagem in sorted(os.listdir(imagens)):
        imagemPronta = tratamento(imagem)
        analisar(imagemPronta, csv=arquivoCSVresultante, classe=classesDasImagens[indiceDaImagem])
        indiceDaImagem += 1


def analisar(imagem, csv, classe=0):
    arrayVolume = sitk.GetArrayFromImage(imagem)
    resolucao = imagem.GetSize() # ROI Original

    ladoX = (resolucao[0]-2) // 10
    ladoY = (resolucao[1]-2) // 10

    global naPrimeiraLinha
    index = 0

    for x in range(10):
        for y in range(10):

            beginx = x * ladoX
            beginy = y * ladoY

            endx = beginx + ladoX
            endy = beginy + ladoY

            voxel = arrayVolume[beginy:endy, beginx:endx]

            voxel = sitk.GetImageFromArray(voxel)

            voxelVolume  = volumetrizar(voxel)              # Voxelização do pixel
            resultado    = extrator(voxelVolume)            # Extração das características do voxel

            # Resultados numericos
            valores     = [valor for _, valor in six.iteritems(resultado)][37:]
            valores     = [0.0  if str(valor) == "nan" else valor for valor in valores]

            classeDaImagem = str(classe)

            # Os títulos das colunas devem ser adicionados somente no início do documento.
            if naPrimeiraLinha:           
                extratores  = [str(nome) for nome, _ in six.iteritems(resultado)][37:]
                extratores += ["class"]
                escreverNoCSV(csv, extratores)
                naPrimeiraLinha = False # Agora, já não haverá mais tal registro

            escreverNoCSV(csv, valores + [classeDaImagem])

            # Registro dos resultados na tela, para debugging
            # for i in range(len(resultado)-37):
            #    print(str(extratores[i]) + "\t" + str(valores[i]))

            index += 1
            print(f" \t>> \t {(index):3.0f}% concluido.\t [Voxel ([{beginx} - {endx}], [{beginy} - {endy}])] \t Classe: {classeDaImagem} ", end="\r")


def extrator(volume):
    mask = np.zeros((volume.GetDepth(),volume.GetHeight(),volume.GetWidth()))
    mask[1,:,:] = 1

    mask = sitk.GetImageFromArray(mask)

    extrator = radiomics.featureextractor.RadiomicsFeatureExtractor(parametros)
    return extrator.execute(volume, mask)


def escreverNoCSV(arquivoCSV, conteudo=["", ""], fim="\n"):
    for item in conteudo:
        arquivoCSV.write(str(item) + ";")

    arquivoCSV.write(fim)


def volumetrizar(imagemOriginal):
    # Funções para volumetrização
    tileFilter = sitk.TileImageFilter()     
    tileFilter.SetLayout([1,1,0])           
    tileFilter.SetDefaultPixelValue(0)

    volume = sitk.JoinSeries(imagemOriginal)
    return tileFilter.Execute(volume, volume, volume)  


def tratamento(imagem):
    # Leitura da imagem
    imagemOriginal = cv2.imread(os.path.join(diretorio, imagem))

    # Parâmetros do pré-processamento
    maxValues       = 255
    BrilhoEfetivo   = 0
    Alpha           = float(131 * (contraste + 127)) / (127 * (131 - contraste))
    Gamma           = 127 * (1 - Alpha)

    # Brilho:
    if brilho != 0:
        if brilho > 0:
            BrilhoEfetivo = brilho
        else:
            maxValues += brilho

        imagemProcessada = cv2.addWeighted(imagemOriginal, (maxValues - BrilhoEfetivo) / 255, imagemOriginal, 0, BrilhoEfetivo)

    else:
        imagemProcessada = imagemOriginal
  
    # Contraste:
    if contraste != 0:
        imagemProcessada = cv2.addWeighted(imagemProcessada, Alpha, imagemProcessada, 0, Gamma)

    # Resolução de overflow, caso ocorra
    hsvImage = cv2.cvtColor(imagemProcessada, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsvImage)
    v[v > 255] = 255
    v[v < 0] = 0
    hsvImage = cv2.merge((h, s, v))
    imagemProcessada = cv2.cvtColor(cv2.cvtColor(hsvImage, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
    imagemProcessada = sitk.GetImageFromArray( np.array(imagemProcessada) )

    print(f"\n\n\t- Pre-processamento de {str(imagem)} concluido.\n\n\tProgresso da extração:")
    
    return imagemProcessada


naPrimeiraLinha = True
if __name__ == "__main__":
    main()
