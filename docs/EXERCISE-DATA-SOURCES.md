# Fontes abertas de exercícios para o TYVON

Atualizado em outubro de 2026.

## Objetivo

O TYVON não deve depender de uma lista artesanal pequena de exercícios. A biblioteca interna pode crescer usando datasets abertos, desde que a licença, a qualidade dos metadados e a compatibilidade com o produto sejam verificadas antes de importar imagens ou instruções.

## Fontes pesquisadas

### free-exercise-db

Repositório:
https://github.com/yuhonas/free-exercise-db

Pontos úteis:
- 800+ exercícios;
- JSON estruturado;
- músculos primários e secundários;
- equipamento;
- nível;
- mecânica do movimento;
- instruções;
- imagens;
- conteúdo declarado como domínio público.

Uso recomendado:
Base inicial para ampliar catálogo e mapear variações de exercícios.

### wger

Repositório:
https://github.com/wger-project/wger

Pontos úteis:
- projeto FLOSS maduro;
- API REST pública para exercícios;
- taxonomia de exercícios e equipamentos;
- suporte a rotinas;
- boa referência arquitetural para biblioteca de exercícios.

Uso recomendado:
Referência para modelagem e eventual importação periódica de dados compatíveis.

### exercemus/exercises

Repositório:
https://github.com/exercemus/exercises

Pontos úteis:
- aliases;
- instruções;
- dicas;
- equipamento;
- músculos primários e secundários;
- tempo;
- imagens.

Uso recomendado:
Boa fonte para normalizar nomes e aliases de exercícios.

### kinetic-place/exercises-db

Repositório:
https://github.com/kinetic-place/exercises-db

Pontos úteis:
- 899+ exercícios;
- grupos musculares;
- equipamentos;
- mídia;
- classificação de músculos primários, secundários e terciários.

Uso recomendado:
Referência para relacionar exercício, equipamento e músculos.

## Decisão atual

Nesta release o TYVON não consome dados remotos desses repositórios em runtime.

Motivos:
- evita dependência externa durante o treino;
- mantém o app funcionando mesmo sem acesso a terceiros;
- evita quebrar a CSP atual;
- permite revisar licença e conteúdo antes de importar mídia;
- mantém nomes em português e a experiência consistente.

A biblioteca interna foi ampliada e estruturada para receber uma importação futura.

## Próxima etapa recomendada

Criar um script de importação offline que:
1. baixa um dataset aberto aprovado;
2. normaliza nomes, músculos, equipamentos e aliases;
3. remove duplicatas;
4. mantém apenas exercícios de força relevantes ao produto;
5. gera um JSON versionado dentro do TYVON;
6. nunca depende do GitHub durante uma sessão de treino.
