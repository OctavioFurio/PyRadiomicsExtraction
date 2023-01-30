
# V2.1 - Extração radiomica de imagens .tif
# 30.01.23

from __future__ import print_function
from radiomics import featureextractor, getFeatureClasses

import logging
import os
import sys
import six
import gc
import radiomics
import nrrd

import numpy as np
import pandas as pd
import SimpleITK as sitk

# Leitura do arquivo NRRD com a característica e coloca numa matriz
def readNrrdData(filename): 
        data, header = nrrd.read(filename)
        voxels = []
        for x in range(data.shape[0]):
            for y in range(data.shape[1]):
                for z in range(data.shape[2]):
                    if not np.isnan(data[x, y, z]):
                        voxels.append(data[x, y, z])
        return voxels



def addDimension(image):
    imagem = sitk.ReadImage(image)
    layers = 10

    eixo_x, eixo_z = imagem.GetWidth(), imagem.GetHeight()
    volume = sitk.Image([eixo_x, layers, eixo_z], imagem.GetPixelID())

    for i in range(layers):
        imagem = sitk.PermuteAxes(sitk.JoinSeries([sitk.ReadImage(image)]),[0,2,1])
        volume = sitk.Paste(volume, imagem, [eixo_x, 1, eixo_z], [0,0,0], [0,i,0])

    sitk.WriteImage(volume, str(image).lstrip("/")[0] + '.nrrd')
    
    return volume



def main():    
    Diretorio, Parametros, Log = sys.argv[1], sys.argv[2], sys.argv[3]

    settings = {'label': 160}

    # Extrator
    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(Parametros, additionalInfo=True, **settings)
    featureClasses = getFeatureClasses()

    # Extração de características Radiômicas por voxel
    for diretorio, _, arquivos in os.walk(Diretorio):
        for arquivo in arquivos:
            f_name = arquivo.split('.')
            try:
                mask = image = addDimension(diretorio+'/'+arquivo)
                featureVector = extractor.execute(image, mask, voxelBased=True)
                for featureName, featureValue in six.iteritems(featureVector):
                    if isinstance(featureValue, sitk.Image):
                        sitk.WriteImage(100 * featureValue, "C:/ResultsFromPyrad" +'/%s-%s.nrrd'%(f_name[0], featureName)) #coloca o resultado da extração da feature num arquivo nrrd
            except OSError as error:
                pass

    # Diretorio com os arquivos NRRD contendo o resultado
    Diretorio = r"C:/ResultsFromPyrad"

    for diretorio, subDiretorios, arquivos in os.walk(Diretorio): 
        df = pd.DataFrame()
        patient_code = ''
        for arquivo in arquivos:
            split = arquivo.split('-')
            # Id
            patient_code = split[0] 
            
            # Nome da feature
            feature_name = split[1].split('.nrrd') 
            features = readNrrdData(diretorio+'/'+arquivo)
            
            # Coloca a matriz num dataframe
            df[feature_name[0]] = pd.Series(features) 
            
            # Exporta as features para csv
            df.to_csv("C:/ResultsFromPyrad/" + patient_code + '_features.csv', index = False)



if __name__ == "__main__":
    main()