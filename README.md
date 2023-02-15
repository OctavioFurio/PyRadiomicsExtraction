# PyRadiomicsExtraction

## Sumário:

- [Execução](https://github.com/OctavioFurio/PyRadiomicsExtraction#execu%C3%A7%C3%A3o)
- [Funcionamento](https://github.com/OctavioFurio/PyRadiomicsExtraction#funcionamento)
- [Pré-Processamento](https://github.com/OctavioFurio/PyRadiomicsExtraction#pr%C3%A9-processamento)
- [Dependências](https://github.com/OctavioFurio/PyRadiomicsExtraction#depend%C3%AAncias)

### Execução:

Execução via terminal:

    python {{{extrator}}} {{{/diretório_com_imagens}}} {{{parametros}}} (Brilho) (Contraste)
    
*Parâmetros entre parênteses são opcionais, com valores padrão 0 (sem efeitos).

O arquivo resultante por padrão estará no formato .CSV, e será salvo no diretório onde o extrator for executado, com padrão de nome: 

> {{{/diretório_com_imagens}}}_features.csv

Um arquivo adicional será criado, contendo algumas informações adicionais a respeito da extração, com padrão de nome:

> Log_{{{/diretório_com_imagens}}}.txt

### Funcionamento:

```mermaid
%%{ init: { 'flowchart': { 'curve': 'bump' } } }%%
flowchart TB

    inputs[[Execução]]

    inputs -.-> dir[(Diretório com imagens)]
    inputs .-> add{{Parâmetros}}
    inputs -. Dados adicionais .-> br([Brilho & Contraste])   
    dir --> pp{{Pré-Processamento}}
    add ---> pr([PyRadiomics])
    br --> pp

    subgraph extrator.py
        pp == Imagens Tratadas ==> dim(Volumetrização)
        dim == Novo Volume ==> pr    
    end
    
    subgraph Resultados
    pr -- Características extraídas --> Diretório_features.csv
    log_Diretório.txt
    end
    
    extrator.py -. Dados Diagnósticos .-> log_Diretório.txt
```

### Pré-processamento

É possível, se necessário, alterar significativamente o Brilho e Contraste das imagens, registrando-se no ato da execução os valores a serem utilizados pelo programa.
É recomendado que estejam no intervalo [-100, 100], para evitar um comportamento destrutivo do pré-processamento nas imagens.

    python {{{extrator}}} {{{/diretório_com_imagens}}} {{{parametros}}} (Brilho) (Contraste)

O ajuste desses parâmetros alterará **todas** as imagens do diretório durante a extração.
Recomenda-se a alteração destes parâmetros vide testes com as imagens.

Seguem imagens com diferentes níveis de cada parâmetro:

|  Parâmetro  |     -100     |     -50     |     0     |     50     | 100         |
|:------:|:------------:|:-----------:|:---------:|:----------:|-------------|
| Brilho | ![C0B-100](https://user-images.githubusercontent.com/103672525/217923136-fe14e8e0-1bb0-4c90-b527-38c6c13199c8.jpg) | ![C0B-50](https://user-images.githubusercontent.com/103672525/217923179-3e8debdf-e15c-472b-9538-00675ed5b7c3.jpg) | ![C0B0](https://user-images.githubusercontent.com/103672525/217923328-aad5bcb3-bdde-485d-85d8-7701ff2f6bd7.jpg) | ![C0B50](https://user-images.githubusercontent.com/103672525/217923218-e641cd20-b3f7-4c43-b80f-eeccfd3de9f4.jpg) | ![C0B100](https://user-images.githubusercontent.com/103672525/217923257-62f703ee-7562-4454-9145-dcca5ecfac3f.jpg) |

|  Parâmetro |       0      |      50     |    100    |
|:---------:|:------------:|:-----------:|:---------:|
| Contraste | ![C0B0](https://user-images.githubusercontent.com/103672525/217923328-aad5bcb3-bdde-485d-85d8-7701ff2f6bd7.jpg) | ![C50B0](https://user-images.githubusercontent.com/103672525/217922969-fbee820d-0aa7-42fe-92e5-4d128fd5b0e4.jpg) | ![C100B0](https://user-images.githubusercontent.com/103672525/217922999-3e25d03a-5d80-496f-8aab-7a8d5582fc77.jpg) |


### Dependências:

- datetime
- gc
- numpy
- OpenCV
- pandas
- radiomics
- SimpleITK
- six
- timeit
