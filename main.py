import streamlit as st
import pandas as pd
from datetime import datetime, time
import sqlite3
import hashlib
import smtplib
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import datetime
import random
import string
import warnings



# Suprime especificamente a mensagem de aviso do Streamlit
warnings.filterwarnings("ignore", message="Please replace st.experimental_get_query_params with st.query_params.")

# Configura a página do Streamlit - ESSA LINHA DEVE SER A PRIMEIRA CHAMADA AO STREAMLIT
st.set_page_config(layout='wide', page_title="Frota Vilaurbe", page_icon=":car:")




# Função para gerar um token aleatório
def gerar_token_tamanho_aleatorio(tamanho=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))



# Inicializa o cache de reservas se não existir
if 'reservas' not in st.session_state:
    st.session_state.reservas = []

# Inicializa a variável de controle de usuário logado
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

# Inicializa a variável de controle da página atual
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
    
# Inicializa a variável de controle de nome completo
if 'nome_completo' not in st.session_state:
    st.session_state.nome_completo = None
    
    
# Função para recuperar a senha
def recuperar_senha(email):
    token = gerar_token_tamanho_aleatorio()
    salvar_token_no_banco(email, token)
    link = f'http://localhost:8502/?token={token}'
    enviar_email_recovery(email, link)
    
    
    
def resetar_senha():
    st.title('Redefinir Senha')
    
    # Capture os parâmetros da URL usando st.query_params
    query_params = st.query_params
    
    # Exiba todos os parâmetros para depuração
    st.write(f'Todos os parâmetros da URL: {query_params}')
    
    # Captura o token corretamente da lista
    token = query_params.get('token', [None])[0]
    
    # Remova espaços em branco e verifique o token
    token = token.strip() if token else None
    
    # Verifique o valor do token capturado
    st.write(f'Token capturado da URL: {token}')
    
    if not token:
        st.error("Token inválido ou expirado.")
        return
    
    # Adicione depuração para a consulta SQL
    st.write(f'Executando consulta com token: {token}')
    
    # Busca o email associado ao token
    with sqlite3.connect('reservas.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM tokens WHERE token = ?', (token,))
        result = cursor.fetchone()
    
    st.write(f'Resultado da consulta: {result}')
    
    if result:
        email = result[0]
        st.text_input("E-mail", value=email, disabled=True)
        
        nova_senha = st.text_input("Nova Senha", type="password", placeholder="Digite sua nova senha")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Confirme sua nova senha")

        if st.button("Redefinir Senha"):
            if nova_senha != confirmar_senha:
                st.error("As senhas não correspondem.")
            else:
                if atualizar_senha_com_token(token, nova_senha):
                    st.success("Senha redefinida com sucesso!")
                    st.info("Agora você pode fazer login com sua nova senha.")
    else:
        st.error("Token inválido ou expirado.")





def salvar_token_no_banco(email, token):
    try:
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO tokens (email, token) VALUES (?, ?)''', (email, token))
            conn.commit()
            
    except Exception as e:
        print(f'Erro ao salvar token no banco de dados: {e}')




def enviar_email_recovery(destinatario, link):
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    remetente = 'ti@vilaurbe.com.br'
    senha = 'Vilaurbe2024!'

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = 'Frota Vilaurbe - Recuperação de Senha'
        
        corpo_email = f'Acesse o Link a seguir para cadastrar uma nova senha: {link}'
        msg.attach(MIMEText(corpo_email, 'plain'))
        
        with smtplib.SMTP(servidor_smtp, porta) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())

        print("Email enviado com sucesso!")
    except Exception as e:
        print(f'Erro ao enviar email: {e}')
        

def resetar_senha():
    st.title('Redefinir Senha')
    
    # Continue usando st.experimental_get_query_params
    query_params = st.experimental_get_query_params()
    
    # Exiba todos os parâmetros para depuração
    st.write(f'Todos os parâmetros da URL: {query_params}')
    
    # Captura o token corretamente da lista
    token = query_params.get('token', [None])[0]
    
    # Remova espaços em branco e verifique o token
    token = token.strip() if token else None
    
    # Verifique o valor do token capturado
    st.write(f'Token capturado da URL: {token}')
    
    if not token:
        st.error("Token inválido ou expirado.")
        return
    
    # Adicione depuração para a consulta SQL
    st.write(f'Executando consulta com token: {token}')
    
    # Busca o email associado ao token
    with sqlite3.connect('reservas.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM tokens WHERE token = ?', (token,))
        result = cursor.fetchone()
    
    st.write(f'Resultado da consulta: {result}')
    
    if result:
        email = result[0]
        st.text_input("E-mail", value=email, disabled=True)
        
        nova_senha = st.text_input("Nova Senha", type="password", placeholder="Digite sua nova senha")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Confirme sua nova senha")

        if st.button("Redefinir Senha"):
            if nova_senha != confirmar_senha:
                st.error("As senhas não correspondem.")
            else:
                if atualizar_senha_com_token(token, nova_senha):
                    st.success("Senha redefinida com sucesso!")
                    st.info("Agora você pode fazer login com sua nova senha.")
    else:
        st.error("Token inválido ou expirado.")





    
    
    
        
def recuperar_senha(email):
    token = gerar_token_tamanho_aleatorio()
    salvar_token_no_banco(email, token)
    link = f'http://localhost:8501/?token={token}'
    enviar_email_recovery(email, link)







def enviar_notificacao_reserva(email_usuario, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destinos):
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    remetente = 'ti@vilaurbe.com.br'
    senha = 'Vilaurbe2024!'
    destinatario = 'analytics@vilaurbe.com.br'  # Destinatário da notificação

    # Formatação das datas para o formato DD/MM/YYYY
    dtRetirada_formatada = dtRetirada.strftime('%d/%m/%Y')
    dtDevolucao_formatada = dtDevolucao.strftime('%d/%m/%Y')

    assunto = 'Nova Reserva Realizada'
    corpo = f"""
    Prezado(a),

    Informamos que uma nova reserva foi realizada com sucesso. Seguem os detalhes da reserva:

    - Nome do Usuário: {email_usuario}
    - Data de Retirada: {dtRetirada_formatada}
    - Hora de Retirada: {hrRetirada.strftime('%H:%M')}
    - Data de Devolução: {dtDevolucao_formatada}
    - Hora de Devolução: {hrDevolucao.strftime('%H:%M')}
    - Veículo: {carro}
    - Destinos: {destinos}

    Atenciosamente,

    Equipe Frota Vilaurbe
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto

        msg.attach(MIMEText(corpo, 'plain'))

        with smtplib.SMTP(servidor_smtp, porta) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
        
        print("Notificação de reserva enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar notificação de reserva: {e}")




def enviar_email_reserva(destinatario, nome, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, cidade):
    servidor_smtp = 'smtp.office365.com'
    porta = 587
    remetente = 'ti@vilaurbe.com.br'
    senha = 'Vilaurbe2024!'

    try:
        # Formata as datas para o formato DD/MM/YYYY
        dtRetirada_formatada = dtRetirada.strftime('%d/%m/%Y')
        dtDevolucao_formatada = dtDevolucao.strftime('%d/%m/%Y')

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = 'Confirmação de Reserva'

        corpo = f'''
        Prezado(a) {nome},

        Informamos que sua reserva foi confirmada com sucesso. Seguem os detalhes da sua reserva:

        - Data de Retirada: {dtRetirada_formatada}
        - Hora de Retirada: {hrRetirada.strftime('%H:%M')}
        - Data de Devolução: {dtDevolucao_formatada}
        - Hora de Devolução: {hrDevolucao.strftime('%H:%M')}
        - Veículo: {carro}
        - Cidade de Destino: {cidade}

        Agradecemos por escolher a Frota Vilaurbe. Estamos à disposição para qualquer esclarecimento adicional.

        Atenciosamente,

        Equipe Frota Vilaurbe
        '''

        msg.attach(MIMEText(corpo, 'plain'))

        with smtplib.SMTP(servidor_smtp, porta) as server:
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
        
        print("Email de confirmação de reserva enviado com sucesso!")
    except Exception as e:
        print(f'Erro ao enviar email de reserva: {e}')







def registrar_reserva(nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status):
    try:
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO reservas (nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (nome_completo, email_usuario, dtRetirada, dtDevolucao, hrRetirada, hrDevolucao, carro, cidade, status))
            conn.commit()
            
            dados_reserva = f"Nome: {nome_completo}, Email: {email_usuario}, Data Retirada: {dtRetirada}, Data Devolução: {dtDevolucao}, Hora Retirada: {hrRetirada}, Hora Devolução: {hrDevolucao}, Carro: {carro}, Cidade: {cidade}, Status: {status}"
            enviar_notificacao_reserva(dados_reserva)
            
            print("Reserva registrada e notificação enviada!")
    except Exception as e:
        print(f"Falha ao registrar reserva: {e}")




    

# Função para criar tabelas no banco de dados
# Função para criar as tabelas no banco de dados
def criar_tabelas():
    with sqlite3.connect('reservas.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                            id INTEGER PRIMARY KEY,
                            nome_completo TEXT,
                            email TEXT UNIQUE,
                            senha TEXT,
                            token TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS reservas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome_completo TEXT,
                            email_usuario TEXT,
                            dtRetirada DATE,
                            dtDevolucao DATE,
                            hrRetirada TEXT,
                            hrDevolucao TEXT,
                            carro TEXT,
                            cidade TEXT,
                            status TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT,
                            token TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (email) REFERENCES usuarios(email)
                        )''')
        conn.commit()
        
        


# Função para adicionar um novo usuário
def adicionar_usuario(nome_completo, email, senha):
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    try:
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO usuarios (nome_completo, email, senha) VALUES (?, ?, ?)', 
                           (nome_completo, email, senha_hash))
            conn.commit()
    except Exception as e:
        st.error(f'Erro ao adicionar usuário: {e}')

# Função para verificar o usuário
def verificar_usuario(email, senha):
    # Verifica se o email tem o domínio correto
    if not email.endswith('@vilaurbe.com.br'):
        st.error("Acesso restrito. Apenas colaboradores são permitidos.")
        return False
    
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    with sqlite3.connect('reservas.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nome_completo, email FROM usuarios WHERE email = ? AND senha = ?', (email, senha_hash))
        usuario = cursor.fetchone()
        if usuario:
            st.session_state.usuario_logado = usuario[1]
            st.session_state.nome_completo = usuario[0]
            return True
        else:
            return False




# Função para atualizar a senha do usuário
def atualizar_senha(email, nova_senha):
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    try:
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE usuarios SET senha = ? WHERE email = ?', (senha_hash, email))
            conn.commit()
            if cursor.rowcount == 0:
                st.error("Nenhum usuário encontrado com o e-mail fornecido.")
                return False
            return True
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar a senha: {e}")
        return False

# Função de login
def login():
    st.markdown('', unsafe_allow_html=True)
    st.subheader('Login')
    email = st.text_input('E-mail', placeholder='Digite seu e-mail')
    senha = st.text_input('Senha', type='password', placeholder='Digite sua senha')
    if st.button('Entrar'):
        if verificar_usuario(email, senha):
            st.success('Login bem-sucedido!')
            st.session_state.pagina = 'home'
        else:
            st.error('E-mail ou senha incorretos.')

# Função de cadastro
def cadastro():
    st.markdown('<div style="background-color:#f0f2f6;padding:20px;border-radius:8px;">', unsafe_allow_html=True)
    st.subheader('Cadastro')
    nome_completo = st.text_input('Nome Completo', placeholder='Digite seu nome completo')
    email = st.text_input('E-mail', placeholder='Digite seu e-mail')
    senha = st.text_input('Senha', type='password', placeholder='Digite sua senha')
    confirmar_senha = st.text_input('Confirme a Senha', type='password', placeholder='Confirme sua senha')
    
    if st.button('Cadastrar'):
        if senha == confirmar_senha:
            # Verifica se o e-mail pertence ao domínio vilaurbe.com.br
            if email.endswith('@vilaurbe.com.br'):
                if adicionar_usuario(nome_completo, email, senha):
                    st.success('Cadastro realizado com sucesso!')
                else:
                    st.error('E-mail já cadastrado.')
            else:
                st.error('Somente para colaboradores "vilaurbe" são permitidos.')
        else:
            st.error('As senhas não correspondem.')
    st.markdown('</div>', unsafe_allow_html=True)








# Função para arredondar a hora para o intervalo mais próximo
def arredondar_para_intervalo(time_obj, intervalo_mins=30):
    total_mins = time_obj.hour * 60 + time_obj.minute
    arredondado = round(total_mins / intervalo_mins) * intervalo_mins
    horas = arredondado // 60
    minutos = arredondado % 60
    return time(horas, minutos)

# Função para adicionar uma nova reserva
def adicionar_reserva(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destinos):
    try:
        destino_str = ', '.join(destinos) if destinos else ''
        if veiculo_disponivel(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro):
            with sqlite3.connect('reservas.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO reservas 
                                  (nome_completo, email_usuario, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, cidade, status) 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (st.session_state.nome_completo, st.session_state.usuario_logado, 
                                dtRetirada.strftime('%d/%m/%Y'), hrRetirada.strftime('%H:%M:%S'), 
                                dtDevolucao.strftime('%d/%m/%Y'), hrDevolucao.strftime('%H:%M:%S'), 
                                carro, destino_str, 'Agendado'))
                conn.commit()
            enviar_notificacao_reserva(st.session_state.nome_completo, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destino_str)
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Erro ao adicionar reserva: {e}")
        return False




# Função para liberar a vaga quando a reserva é cancelada
def liberar_vaga(reserva_id):
    with sqlite3.connect('reservas.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM reservas WHERE id = ?', (reserva_id))
        conn.commit()

# Função para estilizar a visualização de reservas com base no status
def estilizar_reservas(df):
    def aplicar_estilo(status):
        if status == 'Agendado':
            return ['background-color: green']*len(df.columns)
        elif status == 'Em andamento':
            return ['background-color: lightblue']*len(df.columns)
        elif status == 'Concluído':
            return ['background-color: lightgreen']*len(df.columns)
        elif status == 'Cancelado':
            return ['background-color: red']*len(df.columns)
        else:
            return ['']*len(df.columns)
    return df.style.apply(lambda x: aplicar_estilo(x['status']), axis=1)

# Função para carregar reservas do banco
def carregar_reservas_do_banco():
    try:
        with sqlite3.connect('reservas.db') as conn:
            return pd.read_sql_query('SELECT * FROM reservas', conn)
    except Exception as e:
        st.error(f'Erro ao carregar reservas: {e}')
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro


# Função para filtrar reservas com base em critérios específicos
def filtrar_reservas(df, dtRetirada=None, dtDevolucao=None, carros=None, cidades=None):
    if dtRetirada:
        df = df[df['dtRetirada'] == pd.Timestamp(dtRetirada).strftime('%d/%m/%Y')]
    
    if dtDevolucao:
        df = df[df['dtDevolucao'] == pd.Timestamp(dtDevolucao).strftime('%d/%m/%Y'), format]
    
    if carros:
        df = df[df['carro'].str.contains('|'.join(carros), case=False, na=False)]
    
    if cidades:
        df = df[df['cidade'].str.contains('|'.join(cidades), case=False, na=False)]
    
    return df

# Função para buscar reservas aplicando filtros
def buscar_reservas_filtros(dtRetirada=None, dtDevolucao=None, carros=None, cidade=None):
    df_reservas = carregar_reservas_do_banco()
    return filtrar_reservas(df_reservas, dtRetirada, dtDevolucao, carros, cidade,)

# Função para criar DataFrame formatado para visualização
def criar_df_para_visualizacao(df):
    df['dtRetirada'] = pd.to_datetime(df['dtRetirada'], format='%d/%m/%Y')
    df['dtDevolucao'] = pd.to_datetime(df['dtDevolucao'], format='%d/%m/%Y')
    df['hrRetirada'] = pd.to_datetime(df['hrRetirada'], format='%H:%M:%S').dt.time
    df['hrDevolucao'] = pd.to_datetime(df['hrDevolucao'], format='%H:%M:%S').dt.time
    return df

# Função para visualizar reservas na interface
def visualizar_reservas():
    st.markdown('<div style="background-color:#f0f2f6;padding:20px;border-radius:8px;">', unsafe_allow_html=True)
    st.subheader('Visualizar Reservas')

    # Formulário para filtrar reservas
    with st.form(key='filtros'):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            dtRetirada = st.date_input('Data de Retirada')
        with col2:
            dtDevolucao = st.date_input('Data de Devolução')
        with col3:
            carro = st.text_input('Carro')
        with col4:
            cidade = st.text_input('Cidade')

        filtro_aplicado = st.form_submit_button('Buscar')

    if filtro_aplicado:
        df_filtrada = buscar_reservas_filtros(dtRetirada, dtDevolucao, carro, cidade)
        if not df_filtrada.empty:
            df_filtrada = criar_df_para_visualizacao(df_filtrada)
            st.write(estilizar_reservas(df_filtrada))
        else:
            st.error('Nenhuma reserva encontrada.')

    st.markdown('</div>', unsafe_allow_html=True)


# Função para verificar se o veículo está disponível
def veiculo_disponivel(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro):
    df_reservas = carregar_reservas_do_banco()

    # Convertendo as datas das reservas para o formato `datetime.date`
    df_reservas['dtRetirada'] = pd.to_datetime(df_reservas['dtRetirada'], format='%d/%m/%Y').dt.date
    df_reservas['dtDevolucao'] = pd.to_datetime(df_reservas['dtDevolucao'], format='%d/%m/%Y').dt.date
    df_reservas['hrRetirada'] = pd.to_datetime(df_reservas['hrRetirada'], format='%H:%M:%S').dt.time
    df_reservas['hrDevolucao'] = pd.to_datetime(df_reservas['hrDevolucao'], format='%H:%M:%S').dt.time

    dtRetirada_date = pd.to_datetime(dtRetirada).date()
    dtDevolucao_date = pd.to_datetime(dtDevolucao).date()

    for index, row in df_reservas.iterrows():
        if row['carro'] == carro and row['status'] != 'Cancelado':
            if dtRetirada_date <= row['dtDevolucao'] and dtDevolucao_date >= row['dtRetirada']:
                if (hrRetirada >= row['hrRetirada'] and hrRetirada <= row['hrDevolucao']) or \
                   (hrDevolucao >= row['hrRetirada'] and hrDevolucao <= row['hrDevolucao']) or \
                   (hrRetirada <= row['hrRetirada'] and hrDevolucao >= row['hrDevolucao']):
                    return False
    return True


def atualizar_status_reserva(selected_id):
    
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE reservas SET status = "Cancelado"  WHERE id = {selected_id}')
            st.text(type(selected_id))
            conn.commit()
            st.success('Reserva cancelada com sucesso!')
            st.session_state.atualizar_tabela = True
            st.rerun()
   



# Função para adicionar uma nova reserva
def adicionar_reserva(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destinos):
    try:
        if not veiculo_disponivel(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro):
            st.error("O veículo já está reservado para o período selecionado.")
            return
        
        destino_str = ', '.join(destinos) if destinos else ''
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO reservas 
                              (nome_completo, email_usuario, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, cidade, status) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (st.session_state.nome_completo, st.session_state.usuario_logado, 
                            dtRetirada.strftime('%d/%m/%Y'), hrRetirada.strftime('%H:%M:%S'), 
                            dtDevolucao.strftime('%d/%m/%Y'), hrDevolucao.strftime('%H:%M:%S'), 
                            carro, destino_str, 'Agendado'))
            conn.commit()  # Confirma a transação no banco de dados
            st.success("Reserva realizada com sucesso!")  # Mensagem de sucesso exibida após a confirmação
            
            # Enviar a notificação apenas se a reserva for concluída com sucesso
            enviar_notificacao_reserva(st.session_state.nome_completo, dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, carro, destino_str)
            
    except sqlite3.Error as e:
        st.error(f"Erro ao adicionar reserva: {e}")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")







    

# Função para exibir reservas na interface
def exibir_reservas_interativas():
    df_reservas = carregar_reservas_do_banco()
    
    if not df_reservas.empty:
        df_reservas = df_reservas.rename(columns={
            'nome_completo': 'Nome Completo',
            'dtRetirada': 'Data Retirada',
            'hrRetirada': 'Hora Retirada',
            'dtDevolucao': 'Data Devolução',
            'hrDevolucao': 'Hora Devolução',
            'carro': 'Carro',
            'cidade': 'Destino',
            'status': 'Status'
        })

        df_reservas = df_reservas[['id', 'Nome Completo', 'Data Retirada', 'Hora Retirada', 'Data Devolução', 'Hora Devolução', 'Carro', 'Destino', 'Status']]
        df_reservas = df_reservas.sort_values(by='id', ascending=False)

        gb = GridOptionsBuilder.from_dataframe(df_reservas)
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        gb.configure_grid_options(domLayout='normal')  # Ajuste automático de altura
        gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)  # Permite que as colunas sejam redimensionadas
        gb.configure_column("id", width=55)  # Define a largura das colunas específicas, ajuste conforme necessário
        gb.configure_column("Nome Completo", width=170)
        gb.configure_column("Carro", width=170)
        gb.configure_column("Destino", width=210)
        gb.configure_column("Status", width=100)
        gb.configure_column("Data Retirada", width=88)
        gb.configure_column("Hora Retirada", width=80)
        gb.configure_column("Data Devolução", width=88)
        gb.configure_column("Hora Devolução", width=80)
        grid_options = gb.build()

        grid_response = AgGrid(df_reservas, gridOptions=grid_options, update_mode=GridUpdateMode.SELECTION_CHANGED, key='reservas_grid')
        selected_rows = grid_response.get('selected_rows', [])

        
        # Validar se o usuário selecionou um registro:
        if selected_rows is None:
            pass
        else:
            selected_id = selected_rows.iloc[0,0]
        
            
            
            btnCancelar = st.button('Cancelar', key='bntCancelar')
            
            
            # Exibir o botão de Cancelar
            if btnCancelar:
                if atualizar_status_reserva(selected_id):
                    st.success('Status da reserva alterado com sucesso')
                    
                    # Recarregar os dados atualizados
                    df_reservas = carregar_reservas_do_banco()
                    st.session_state.df_selecao = df_reservas
                else:
                    st.error('Erro ao alterar o status da reserva.')
                    
    else:
        st.warning('Nenhuma reserva selecionada')

def verificar_tabelas():
    with sqlite3.connect('reservas.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        st.write('Tabelas existentes:', tables)

        for table_name in [t[0] for t in tables]:
            st.write(f'Colunas da tabela {table_name}:')
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                st.write(f'  {column[1]}')



    


# Função para limpar o banco de dados
def limpar_banco_dados():
    try:
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS reservas;")
            cursor.execute("DROP TABLE IF EXISTS usuarios;")
            conn.commit()
            criar_tabelas()
    except sqlite3.OperationalError as e:
        st.error(f"Erro ao acessar o banco de dados: {e}")
        
        
        
        
def recuperar_senha(email):
    token = gerar_token_tamanho_aleatorio()
    salvar_token_no_banco(email, token)
    link = f'http://localhost:8501/?token={token}'
    enviar_email_recovery(email, link)


    enviar_email_recovery(email, link)

def atualizar_senha_com_token(token, nova_senha):
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    try:
        with sqlite3.connect('reservas.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE usuarios SET senha = ? 
                              WHERE email = (SELECT email FROM tokens WHERE token = ?)''', 
                           (senha_hash, token))
            cursor.execute('DELETE FROM tokens WHERE token = ?', (token,))
            conn.commit()
            if cursor.rowcount == 0:
                st.error("Token inválido ou expirado.")
                return False
            return True
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar a senha: {e}")
        return False




# Página para redefinir a senha
def resetar_senha():
    st.title('Redefinir Senha')
    query_params = st.experimental_get_query_params()
    token = query_params.get('token', [None])[0]
    
    

    if not token:
        st.error("Token inválido ou expirado.")
        return
    
    # Busque o email associado ao token
    with sqlite3.connect('reservas.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM tokens WHERE token = ?', (token,))
        result = cursor.fetchone()
    
    if result:
        email = result[0]
        st.text_input("E-mail", value=email, disabled=True)  # Exibe o email fixo e desabilitado para edição
    else:
        st.error("Token inválido ou expirado.")
        return

    nova_senha = st.text_input("Nova Senha", type="password", placeholder="Digite sua nova senha")
    confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Confirme sua nova senha")

    if st.button("Redefinir Senha"):
        if nova_senha != confirmar_senha:
            st.error("As senhas não correspondem.")
        else:
            if atualizar_senha_com_token(token, nova_senha):
                st.success("Senha redefinida com sucesso!")
                st.info("Agora você pode fazer login com sua nova senha.")



def home_page():
    criar_tabelas()
    
    st.sidebar.image('logo.png', use_column_width=True)

    if st.session_state.get('usuario_logado'):
        st.sidebar.header('Administração')
        if st.sidebar.button('Limpar Banco de Dados'):
            limpar_banco_dados()
            st.session_state.clear()
            st.experimental_set_query_params(pagina='home')

        with st.container(border=True):
            st.title('Reserva')
            col1, col2 = st.columns(2)

            with col1:
                dtRetirada = st.date_input(label='Data de Retirada', key='dtRetirada', value=datetime.now(), format='DD/MM/YYYY')
                hrRetirada = st.time_input(label='Hora de Retirada', key='hrRetirada', value=time(9, 0))

            with col2:
                dtDevolucao = st.date_input(label='Data de Devolução', key='dtDevolucao', value=datetime.now(), format='DD/MM/YYYY')
                hrDevolucao = st.time_input(label='Hora de Devolução', key='hrDevolucao', value=time(9, 0))

            nome_completo = st.session_state.nome_completo
            email_usuario = st.session_state.usuario_logado
            descVeiculo = st.selectbox(label='Carro', key='carro', options=[
                'SWQ1F92 - Versa Advance', 'SVO6A16 - Saveiro', 'GEZ5262 - Nissan SV'
            ])
            descDestino = st.multiselect(label='Cidade', key='destino', options=[
                'Rio Claro', 'Lençóis Paulista', 'São Carlos', 'Araras', 'Ribeirão Preto',
                'Jaboticabal', 'Araraquara', 'Leme', 'Piracicaba', 'São Paulo',
                'Campinas', 'Ibate', 'Porto Ferreira'
            ])
            
            hoje = datetime.now().date()
            if not (dtRetirada and hrRetirada and dtDevolucao and hrDevolucao and descVeiculo and descDestino):
                btnCadastrar = st.button('Cadastrar', key='botao_cadastrar', disabled=True)
            else:
                btnCadastrar = st.button('Cadastrar', key='botao_cadastrar', disabled=False)
                if btnCadastrar:
                    if dtRetirada < hoje or dtDevolucao < hoje:
                        st.error('Não é possível fazer uma reserva para uma data passada.')
                    elif dtDevolucao < dtRetirada:
                        st.error('A data de devolução não pode ser anterior à data de retirada.')
                    else:
                        adicionar_reserva(dtRetirada, hrRetirada, dtDevolucao, hrDevolucao, descVeiculo, descDestino)
                        st.success('Reserva realizada com sucesso!')
                                     
        with st.form(key='buscar_reserva'):
            st.subheader('Consultar Reservas')
            col1, col2 = st.columns(2)

            with col1:
                dtRetirada = st.date_input(label='Data de Retirada', key='dtRetirada_filtro', value=None)

            with col2:
                dtDevolucao = st.date_input(label='Data de Devolução', key='dtDevolucao_filtro', value=None)

            col3, col4 = st.columns(2)

            with col3:
                carro = st.multiselect(label='Carro', key='carro_filtro', options=['SWQ1F92 - Nissan Versa Novo', 'SVO6A16 - Saveiro', 'GEZ5262 - Nissan Versa'])

            with col4:
                cidade = st.multiselect(label='Cidade', key='cidade_filtro', options=['Rio Claro', 'Lençóis Paulista', 'São Carlos', 'Araras', 'Ribeirão Preto',
                                                                                    'Jaboticabal', 'Araraquara', 'Leme', 'Piracicaba', 'São Paulo', 'Campinas', 'Ibate', 'Porto Ferreira'])

            buscar_reserva = st.form_submit_button(label='Buscar Reserva')

            if buscar_reserva:
                df_reservas = buscar_reservas_filtros(dtRetirada, dtDevolucao, carro, cidade)
                if df_reservas.empty:
                    st.error('Nenhuma reserva encontrada.')
                else:
                    df_selecao = criar_df_para_visualizacao(df_reservas)
                    st.dataframe(df_selecao)
                    st.session_state.df_selecao = df_selecao

        st.title('Todas as Reservas')
        exibir_reservas_interativas()

    else:
        menu_autenticacao = st.sidebar.radio('Selecione uma opção', ['Login', 'Cadastro', 'Recuperar Senha'])



                
        if menu_autenticacao == 'Login':
            login()
        elif menu_autenticacao == 'Cadastro':
            cadastro()
        elif menu_autenticacao == 'Recuperar Senha':
            email = st.text_input("Digite seu email:")
            if st.button("Recuperar Senha"):
                if email:
                    recuperar_senha(email)
                    st.success("Um email com link de recuperação foi enviado!")


# Exibe a página inicial ou outras páginas
# Detectar se o token está presente nos parâmetros da URL
# Exibe a página inicial ou outras páginas
query_params = st.experimental_get_query_params()

if 'token' in query_params:
    resetar_senha()
else:
    if st.session_state.get('pagina') == 'home':
        home_page()
    elif st.session_state.get('pagina') == 'reservas':
        st.title('Todas as Reservas')
        exibir_reservas_interativas()
        if st.button('Voltar'):
            st.session_state.pagina = 'home'
            st.set_query_params(pagina='home')
    else:
        home_page()