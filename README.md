# PyRadiomicsExtraction

Execução via terminal:

> **python {{{extrator}}} {{{/diretório_com_imagens}}} {{{parametros}}} {{{nome_do_arquivo_resultante}}}**

O arquivo resultante por padrão estará no formato .arff.

## Dependências:

- logging
- os
- sys
- six
- gc
- radiomics
- nrrd
- numpy
- pandas
- SimpleITK

### Dependências específicas:

v2.1 - Necessária a criação de diretório ***C:/ResultsFromPyrad/*** para armazenamento dos arquivos .nrrd com as características extraídas.
