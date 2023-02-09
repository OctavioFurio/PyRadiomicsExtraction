# PyRadiomicsExtraction

Execução via terminal:

    python {{{extrator}}} {{{/diretório_com_imagens}}} {{{parametros}}} (Brilho) (Contraste)
    
*Parâmetros entre parênteses são opcionais, com valores padrão 0 (sem efeitos).

O arquivo resultante por padrão estará no formato .CSV, e será salvo no diretório onde o extrator for executado, com padrão de nome: 

> {{{/diretório_com_imagens}}}_features.csv

### Funcionamento:

```mermaid
flowchart TB
  id1["Diretório"] --Imagens---> Extrator
  id1["Diretório"] --> Params.yaml
  
  subgraph Extrator.py
  Extrator --addDimension--> Volume
  Volume & Params.yaml --> PyRadiomics
  PyRadiomics --> FileSave
  end
  
  FileSave --> Diretório_features.csv
```

## Pré-processamento

É possível, se necessário, alterar significativamente o Brilho e Contraste das imagens, registrando-se no ato da execução os valores a serem utilizados pelo programa, dado que estejam respectivamente no intervalo [-100, 100] e [0, 100].

    python {{{extrator}}} {{{/diretório_com_imagens}}} {{{parametros}}} (Brilho) (Contraste)

O ajuste desses parâmetros alterará **todas** as imagens do diretório durante a extração.
Recomenda-se a alteração destes parâmetros vide testes com as imagens.

Exemplos:

|  Parâmetro |       0      |      50     |    100    |
|:---------:|:------------:|:-----------:|:---------:|
| Contraste | ![C0B0](https://user-images.githubusercontent.com/103672525/217923328-aad5bcb3-bdde-485d-85d8-7701ff2f6bd7.jpg) | ![C50B0](https://user-images.githubusercontent.com/103672525/217922969-fbee820d-0aa7-42fe-92e5-4d128fd5b0e4.jpg) | ![C100B0](https://user-images.githubusercontent.com/103672525/217922999-3e25d03a-5d80-496f-8aab-7a8d5582fc77.jpg) |

|  Parâmetro  |     -100     |     -50     |     0     |     50     | 100         |
|:------:|:------------:|:-----------:|:---------:|:----------:|-------------|
| Brilho | ![C0B-100](https://user-images.githubusercontent.com/103672525/217923136-fe14e8e0-1bb0-4c90-b527-38c6c13199c8.jpg) | ![C0B-50](https://user-images.githubusercontent.com/103672525/217923179-3e8debdf-e15c-472b-9538-00675ed5b7c3.jpg) | ![C0B0](https://user-images.githubusercontent.com/103672525/217923328-aad5bcb3-bdde-485d-85d8-7701ff2f6bd7.jpg) | ![C0B50](https://user-images.githubusercontent.com/103672525/217923218-e641cd20-b3f7-4c43-b80f-eeccfd3de9f4.jpg) | ![C0B100](https://user-images.githubusercontent.com/103672525/217923257-62f703ee-7562-4454-9145-dcca5ecfac3f.jpg) |


## Dependências:

- six
- gc
- radiomics
- numpy
- pandas
- SimpleITK

### Dependências específicas:

v2.0 e anteriores - Sem dependências específicas.

v2.1 - Necessária a criação de diretório ***C:/ResultsFromPyrad/*** para armazenamento dos arquivos .nrrd com as características extraídas.

v2.2 e posteriores - Sem dependências específicas.
