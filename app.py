import streamlit as st
import pandas as pd
import time
import os

# Configuración de página de la UNICEN
st.set_page_config(page_title=Trivia Ambiental - UNICEN, page_icon=🌱, layout=centered)

# --- BASE DE DATOS EN MEMORIA (Simulación síncrona para el evento) ---
if 'game_state' not in st.session_state
    st.session_state.game_state = {
        current_question 0,  
        question_start_time 0.0,
        responses [],        
        active_players set()
    }

PREGUNTAS = [
    {
        id 1,
        q ¿Cuántos años dura la carrera de Licenciatura en Diagnóstico y Gestión Ambiental,
        options [3 Años, 4 Años, 5 Años, 6 Años],
        correct 4 Años
    },
    {
        id 2,
        q ¿En qué sectores puede trabajar un egresado de esta carrera,
        options [Solo en escuelas, Únicamente en laboratorios, Desde el sector privado y ONG hasta gobiernos, Solo en municipios],
        correct Desde el sector privado y ONG hasta gobiernos
    },
    {
        id 3,
        q ¿Cuál de las siguientes es una incumbencia profesional del Licenciadoa,
        options [Diseñar puentes y autopistas, Elaborar informes de evaluación de impacto ambiental, Cirugías veterinarias, Programar aplicaciones móviles],
        correct Elaborar informes de evaluación de impacto ambiental
    },
    {
        id 4,
        q ¿En qué año de la carrera se cursan materias como 'Política y Legislación Ambiental' y 'Economía Ambiental',
        options [Primer Año, Segundo Año, Tercer Año, Cuarto Año],
        correct Tercer Año
    },
    {
        id 5,
        q ¿Cuál de estas materias pertenece al bloque de Primer Año,
        options [Geomorfología y Riesgos Naturales, Auditoría Ambiental, Introducción a las Ciencias de la Tierra, Ecología, Regulación y Manejo],
        correct Introducción a las Ciencias de la Tierra
    },
    {
        id 6,
        q 'Ordenación Ambiental del Territorio' y 'Evaluación del Impacto Ambiental' se dictan en,
        options [Primer Año, Segundo Año, Tercer Año, Cuarto Año],
        correct Cuarto Año
    }
]

# Control de roles por URL
query_params = st.query_params
role = query_params.get(role, alumno)
estado = st.session_state.game_state
curr_q = estado[current_question]

# --- VISTA MONITOR DE TV O CONTROLADOR ---
if role in [admin, tv]
    st.title(🌱 PANEL EN VIVO - Trivia FCH UNICEN)
    st.write(### Licenciatura en Diagnóstico y Gestión Ambiental)
    st.markdown(---)
    
    if curr_q == 0
        st.subheader(📢 ¡Esperando participantes!)
        st.info(Escaneá el código QR del stand para ingresar tu nombre y empezar a competir.)
        st.metric(label=Estudiantes conectados, value=len(estado[active_players]))
        
        if role == admin and st.button(🚀 EMPEZAR PARTIDA EN VIVO)
            estado[current_question] = 1
            estado[question_start_time] = time.time()
            st.rerun()
            
    elif curr_q = len(PREGUNTAS)
        pregunta_actual = PREGUNTAS[curr_q - 1]
        st.subheader(fPregunta {curr_q} de {len(PREGUNTAS)})
        st.header(pregunta_actual['q'])
        
        df_respuestas = pd.DataFrame(estado[responses])
        if not df_respuestas.empty
            df_curr = df_respuestas[df_respuestas['pregunta'] == curr_q]
            if not df_curr.empty
                conteo = df_curr['respuesta'].value_counts()
                st.bar_chart(conteo)
                st.write(f💬 Respuestas enviadas {len(df_curr)})
            else
                st.info(Esperando que los chicos elijan sus opciones...)
        else
            st.info(Esperando respuestas...)
            
        if role == admin and st.button(➡️ Avanzar Pregunta)
            estado[current_question] += 1
            estado[question_start_time] = time.time()
            st.rerun()
    else
        st.balloons()
        st.success(🎉 ¡Trivia terminada!)
        st.write(## 🏆 Tabla de Posiciones Final)
        
        df_respuestas = pd.DataFrame(estado[responses])
        if not df_respuestas.empty
            tabla_puntos = df_respuestas.groupby('usuario')['puntos'].sum().reset_index()
            tabla_puntos = tabla_puntos.sort_values(by='puntos', ascending=False).reset_index(drop=True)
            tabla_puntos.index += 1
            st.table(tabla_puntos.head(5))
        
        if role == admin
            st.write(### 📊 Descarga de Métricas de Interacción)
            if not df_respuestas.empty
                csv = df_respuestas.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=📥 Descargar Base de Datos (CSV),
                    data=csv,
                    file_name=metricas_trivia_ambiental.csv,
                    mime=textcsv
                )

# --- VISTA CELULAR DEL ESTUDIANTE ---
else
    st.title(📲 Trivia Ambiental - FCH)
    
    if 'username' not in st.session_state
        st.subheader(¡Demostrá lo que sabés y ganá!)
        username = st.text_input(Tu Nombre o Apodo)
        if st.button(Ingresar a la Trivia 🚀)
            if username.strip()
                st.session_state.username = username.strip()
                estado[active_players].add(username.strip())
                st.rerun()
    else
        username = st.session_state.username
        
        if curr_q == 0
            st.warning(f¡Todo listo {username}! Mirá el proyector del stand, estamos esperando que empiece la ronda...)
            time.sleep(2)
            st.rerun()
            
        elif curr_q = len(PREGUNTAS)
            pregunta_actual = PREGUNTAS[curr_q - 1]
            ya_respondio = any(r['usuario'] == username and r['pregunta'] == curr_q for r in estado[responses])
            
            if ya_respondio
                st.info(⏳ ¡Respuesta enviada! Prestá atención a la pantalla principal para ver los resultados parciales.)
                time.sleep(2)
                st.rerun()
            else
                st.subheader(fPregunta {curr_q})
                st.write(pregunta_actual['q'])
                
                with st.form(key=fform_cel_{curr_q})
                    opcion_elegida = st.radio(Elegí la opción correcta, pregunta_actual['options'])
                    enviar = st.form_submit_button(Enviar ⚡)
                    
                    if enviar
                        tiempo_empleado = time.time() - estado[question_start_time]
                        if tiempo_empleado  0 tiempo_empleado = 1.0
                        
                        es_correcta = (opcion_elegida == pregunta_actual['correct'])
                        
                        # Cálculo de puntos estilo Kahoot! (Velocidad + Acierto)
                        puntos = 0
                        if es_correcta
                            bono = max(0, int((20 - tiempo_empleado)  25))
                            puntos = 500 + bono
                        
                        estado[responses].append({
                            usuario username,
                            pregunta curr_q,
                            respuesta opcion_elegida,
                            es_correcta es_correcta,
                            puntos puntos
                        })
                        st.success(¡Recibido!)
                        st.rerun()
        else
            st.balloons()
            st.success(🏆 ¡Completaste el juego!)
            
            df_respuestas = pd.DataFrame(estado[responses])
            user_pts = df_respuestas[df_respuestas['usuario'] == username]['puntos'].sum()
            st.metric(label=Tu Puntaje Total, value=f{user_pts} Pts)
            
            st.markdown(---)
            st.write(### 📄 ¡Descargá el folleto en tu celular!)
            st.write(Llevate el plan de materias completo de la Licenciatura en Diagnóstico y Gestión Ambiental.)
            
            # Intenta leer el PDF real si existe en la carpeta
            pdf_path = folleto.pdf
            if os.path.exists(pdf_path)
                with open(pdf_path, rb) as file
                    st.download_button(
                        label=📥 Guardar Folleto Oficial (PDF),
                        data=file,
                        file_name=Folleto_Gestion_Ambiental_UNICEN.pdf,
                        mime=applicationpdf
                    )
            else
                # Texto de respaldo si se corre el código sin el archivo PDF físico al lado
                info_backup = Licenciatura en Diagnóstico y