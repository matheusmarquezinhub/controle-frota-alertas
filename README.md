
# Controle de Frota — Alertas Automáticos

Projeto em Python para **monitorar uma frota a partir de um Excel** e gerar **alertas automáticos** de manutenção, uso intenso e avisos importantes.

A ideia é simples:  
em vez de conferir planilhas todo dia, o sistema **avisa quando algo precisa de atenção**.

---

## O que esse projeto faz

Lendo um arquivo Excel, o script:

- avisa quando a **troca de óleo está urgente**
- alerta quando o óleo está **próximo do limite**
- mostra veículos que **rodaram muitos KM**
- identifica **cadastros incompletos**
- lê observações com palavras-chave (ALERTA, URGENTE, etc.)
- exibe os alertas no **terminal** e em **popup (Windows)**

Tudo baseado em regras claras, configuráveis e fáceis de entender.

---

## Estrutura do projeto

```

controle-frota-alertas/
├─ README.md
├─ LICENSE
├─ requirements.txt
├─ .gitignore
├─ data/
│  └─ Controle_Frota_KM_TEMPLATE.xlsx
└─ src/
├─ main.py
├─ config.py
├─ excel_io.py
├─ rules.py
└─ ui.py

````

---

## Sobre os arquivos de dados

- **Controle_Frota_KM_TEMPLATE.xlsx**  
  Template com a estrutura esperada do Excel.  
  Este arquivo é versionado no repositório.

👉 Para usar o projeto:
1. Copie o template  
2. Renomeie para `Controle_Frota_KM.xlsx`  
3. Preencha com seus dados reais  

O arquivo `Controle_Frota_KM.xlsx` **não é versionado** e deve existir apenas no ambiente local.

---

## Requisitos

- Python 3.10 ou superior
- Windows (para popup com `tkinter`)
  - Em outros sistemas, é só usar `--sem-popup`

---

## Instalação

```bash
pip install -r requirements.txt
````

---

## Como executar

⚠️ Execute sempre a partir da **raiz do projeto**.

```bash
python src/main.py
```

Ou informando o caminho do arquivo:

```bash
python src/main.py --arquivo "C:\caminho\Controle_Frota_KM.xlsx"
```

Rodar sem popup:

```bash
python src/main.py --sem-popup
```

---

## Estrutura esperada no Excel

### Aba `Movimentacao`

Colunas:

* `Placa`
* `Modelo`
* `Ano`
* `Responsável`
* `Status`
* `Data de Saída`
* `Data de Retorno`
* `KM Inicial`
* `KM Final`
* `Observações`

---

### Aba `Manutencao`

Colunas:

* `Placa`
* `Tipo` (ex.: `OLEO`)
* `Data`
* `KM`
* `KM Limite`
* `Observações`

---

## Observação sobre o modelo

A identificação do veículo é feita pela placa, que funciona como identificador único neste projeto.


---

## Licença

Este projeto está sob a **MIT License**.
Uso livre para estudar, adaptar e evoluir.

---

## Autor

**Matheus Marquezin**
Analista de Dados | Automação | Python | SQL | Power BI

---

Projeto simples, direto e feito para resolver um problema real.