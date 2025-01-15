# importacao das bibliotecas
import streamlit as st 
import pandas as pd 
import plotly.express as px

# configurar widemode por padrao
st.set_page_config(layout= 'wide')

# formatacao de numeros
def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# importacao dos dados e foramatacao dos dados
dados = pd.read_json('produtos.json')
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

# titulo da aplicacao 
st.title('LEITURA DE DADOS DE API')

# Filtros
# Barra Lateral
st.sidebar.title('Filtros')
# Região
regioes = ['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste','Sul']
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

# Anos
todos_anos = st.sidebar.checkbox('Dados de todo o período',value= True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

# Vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Tabelas
### Tabelas de receita
## por estados
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset=  'Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, 
left_on = 'Local da compra', right_index= True).sort_values('Preço',ascending= False)

## receita mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

## receita por categoria
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending= False)

### Tabelas de quantidade de vendas
# vendas por estado
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# quantidade de vendas mensal
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

# quanridade de vendas por categoria de produtos
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

### Tabelas de vendedores
# vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))

# Graficos
# aba 1
## grafico de mapa - receitas por estados
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False},
                                  title = 'Receita por estado')

## grafico de linhas - receita mensal
fig_receita_mensal = px.line(receita_mensal,
                             x= 'Mes',
                             y= 'Preço',
                             markers= True,
                             range_y= (0,receita_mensal.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title= 'Receita')

## grafico de barras - receita por estado
fig_receita_estados = px.bar(receita_estados.head(),
                             x= 'Local da compra',
                             y= 'Preço',
                             text_auto= True,
                             title= 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title= 'Receita')

## grafico de barras - receita por categoria
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto= True,
                                title= 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title= 'Receita')

# aba 2 
## grafico de mapa - quantidade de vendas por estado
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

## grafico de linhas - quantidade de vendas mensal
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

## grafico de barras - 5 estados com maior quantidade de vendas
fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados')
fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

## grafico de barras - quantidade de vendas por categoria de produto
fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

# Visualizacao em Streamlit
## abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

## aba 1
with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width= True)
        st.plotly_chart(fig_receita_categorias, use_container_width= True)

## aba 2
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width= True)
        st.plotly_chart(fig_vendas_estados, use_container_width= True)
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width= True)
        st.plotly_chart(fig_vendas_categorias, use_container_width= True)

## aba 3
with aba3:
    # input de numero de vendedores
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5) # valor minimo, maximo e valor padrao
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(),'R$'))
        # grafico de receita vendedores
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum',ascending= False).head(qtd_vendedores),
                                        x= 'sum',
                                        y= vendedores[['sum']].sort_values('sum',ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {qtd_vendedores} vendedores (receita)')
        fig_receita_vendedores.update_layout(yaxis_title= "Vendedor")
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        # grafico de vendas vendedores
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count',ascending= False).head(qtd_vendedores),
                                        x= 'count',
                                        y= vendedores[['count']].sort_values('count',ascending= False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        fig_vendas_vendedores.update_layout(yaxis_title= "Vendedor")
        st.plotly_chart(fig_vendas_vendedores)

## apresentacao em dataframe
## st.dataframe(dados)