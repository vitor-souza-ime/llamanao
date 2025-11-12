#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import qi

class NAOOllamaChat:
    def __init__(self, nao_ip="172.15.3.253", nao_port=9559, model_name="llama3", tts_volume=0.1):
        """
        Chat NAO + Ollama Llama local via subprocess
        """
        try:
            print(f"🔗 Conectando ao NAO em {nao_ip}:{nao_port}...")
            
            # Conecta ao NAO
            self.session = qi.Session()
            self.session.connect(f"tcp://{nao_ip}:{nao_port}")
            print("✅ Conectado ao NAO!")
            
            # Inicializa serviços
            self.asr = self.session.service("ALSpeechRecognition")
            self.memory = self.session.service("ALMemory")
            self.tts = self.session.service("ALTextToSpeech")
            
            # Configura idioma
            self.tts.setLanguage("English")
            
            # Configura volume do TTS
            self.tts.setVolume(tts_volume)
            print(f"✅ Volume do TTS configurado para {tts_volume*100:.0f}%")
            
            self.asr.setLanguage("English")
            
            print("✅ Serviços NAO inicializados!")
            
            # Configuração Ollama
            self.model_name = model_name
            
            # Verifica conexão com Ollama
            self.check_ollama_connection()
            
        except Exception as e:
            print(f"❌ Erro ao conectar com NAO: {e}")
            raise

    def check_ollama_connection(self):
        """Verifica se Ollama está disponível e lista modelos"""
        try:
            print(f"🔗 Verificando Ollama CLI...")
            
            # Tenta listar modelos
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                models_output = result.stdout.strip()
                print(f"✅ Ollama CLI disponível!")
                print(f"\n📦 Modelos instalados:")
                print(models_output)
                
                # Verifica se o modelo escolhido existe
                if self.model_name not in models_output:
                    print(f"\n⚠️ Modelo '{self.model_name}' não encontrado!")
                    print(f"💡 Execute: ollama pull {self.model_name}")
                    
                    # Tenta usar o primeiro modelo disponível
                    lines = models_output.split('\n')[1:]  # Pula cabeçalho
                    if lines:
                        first_model = lines[0].split()[0]
                        print(f"⚠️ Usando modelo disponível: {first_model}")
                        self.model_name = first_model
                else:
                    print(f"✅ Usando modelo: {self.model_name}")
            else:
                print(f"❌ Erro ao executar 'ollama list': {result.stderr}")
                raise Exception("Ollama CLI não está funcionando corretamente")
                
        except FileNotFoundError:
            print("❌ Ollama não encontrado! Instale com:")
            print("   curl -fsSL https://ollama.com/install.sh | sh")
            raise
        except subprocess.TimeoutExpired:
            print("❌ Timeout ao verificar Ollama")
            raise
        except Exception as e:
            print(f"❌ Erro ao verificar Ollama: {e}")
            raise

    def speak(self, text):
        """Faz o NAO falar"""
        try:
            print(f"🤖 NAO vai falar: '{text}'")
            print(f"   (tamanho: {len(text)} caracteres)")
            self.tts.say(text)
            time.sleep(0.2)
        except Exception as e:
            print(f"❌ Erro na fala: {e}")

    def listen(self, duration=8.0, extra_vocabulary=None):
        """
        Método de escuta com vocabulário expandido
        """
        try:
            # Vocabulário base expandido
            vocabulary = [
                # Cumprimentos e cortesia
                "hello", "hi", "hey", "good", "morning", "afternoon", "evening",
                "please", "thank", "you", "thanks", "welcome", "sorry",
                
                # Perguntas básicas
                "what", "how", "where", "when", "why", "who", "which", "can", "do", 
                "are", "is", "will", "would", "could", "should",
                
                # Respostas
                "yes", "no", "maybe", "sure", "okay", "right", "wrong", "true", "false",
                
                # Ações e comandos
                "tell", "me", "about", "talk", "speak", "listen", "look", "see",
                "move", "walk", "turn", "stop", "go", "come", "help", "show",
                
                # Objetos e lugares
                "robot", "nao", "computer", "table", "chair", "room", "house", "outside",
                "ball", "red", "blue", "green", "yellow", "black", "white",
                
                # Pessoas e relacionamentos
                "you", "i", "we", "they", "he", "she", "friend", "family", "people",
                
                # Tempo
                "time", "today", "yesterday", "tomorrow", "now", "later", "before", "after",
                "day", "night", "week", "month", "year",
                
                # Números
                "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                
                # Sentimentos e estados
                "happy", "sad", "good", "bad", "great", "fine", "tired", "hungry", "cold", "hot",
                
                # Tópicos de conversa
                "weather", "music", "book", "movie", "food", "game", "sport", "news",
                "work", "school", "learn", "teach", "study", "read", "write",
                
                # Conectores e palavras funcionais
                "and", "or", "but", "because", "if", "then", "also", "too", "very",
                "really", "quite", "just", "only", "all", "some", "many", "few",
                "the", "a", "an", "this", "that", "these", "those",
                
                # Despedidas
                "bye", "goodbye", "see", "later", "stop", "quit", "exit", "end",
                
                # Teste
                "test", "check", "try", "start", "begin"
            ]
            
            if extra_vocabulary:
                vocabulary.extend(extra_vocabulary)
                print(f"   Vocabulário expandido: +{len(extra_vocabulary)} palavras")
            
            print(f"🎤 Escutando por {duration} segundos... (Vocabulário: {len(vocabulary)} palavras)")
            
            # Configura ASR
            self.asr.pause(True)
            self.asr.setVocabulary(vocabulary, False)
            self.asr.pause(False)
            
            # Limpa memória
            self.memory.insertData("WordRecognized", [])
            
            # Subscreve ao ASR
            self.asr.subscribe("Ollama_Chat")
            
            print("   🟢 PODE FALAR AGORA!")
            
            start_time = time.time()
            recognized_words = []
            last_word_time = start_time
            
            try:
                while time.time() - start_time < duration:
                    time.sleep(0.1)
                    
                    # Verifica palavras reconhecidas
                    words_data = self.memory.getData("WordRecognized")
                    
                    if words_data and len(words_data) >= 2:
                        word = words_data[0]
                        confidence = words_data[1] if len(words_data) > 1 else 0.0
                        
                        if (word and word not in recognized_words and 
                            confidence > 0.3 and word != "<...>"):
                            
                            recognized_words.append(word)
                            last_word_time = time.time()
                            print(f"   ✅ '{word}' (conf: {confidence:.2f})")
                            
                            if word.lower() in ["bye", "goodbye", "stop", "quit", "exit", "end"]:
                                print("   🛑 Comando de saída detectado!")
                                break
                    
                    # Para se passou tempo sem novas palavras
                    if recognized_words and (time.time() - last_word_time) > 3.0:
                        print("   ⏸️ Silêncio detectado, processando...")
                        break
                        
            except KeyboardInterrupt:
                print("\n   ⛔ Interrompido pelo usuário")
                
            finally:
                try:
                    self.asr.unsubscribe("Ollama_Chat")
                except:
                    pass
            
            if recognized_words:
                sentence = " ".join(recognized_words)
                print(f"   📝 Frase reconhecida: '{sentence}'")
                return sentence
            else:
                print("   ❌ Nenhuma palavra reconhecida")
                return None
                
        except Exception as e:
            print(f"❌ Erro na escuta: {e}")
            try:
                self.asr.unsubscribe("Ollama_Chat")
            except:
                pass
            return None

    def ask_ollama(self, question: str):
        """
        Processa pergunta com Ollama via subprocess e mede o tempo
        """
        try:
            print(f"🧠 Ollama ({self.model_name}) processando: '{question}'")
            
            # ⏱️ INÍCIO DA MEDIÇÃO
            start_time = time.time()
            
            # Prepara o prompt de forma mais direta
            # Evita que o modelo se re-apresente a cada pergunta
            prompt = f"Answer this briefly in 1-2 sentences: {question}"
            
            # Chama o modelo LLaMA via ollama CLI
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # ⏱️ FIM DA MEDIÇÃO
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                resposta = result.stdout.strip()
                
                # Remove possíveis prefixos do modelo
                if resposta.startswith("Assistant:"):
                    resposta = resposta[10:].strip()
                
                # Limpa tokens especiais
                resposta = resposta.replace("<|im_end|>", "").replace("<|im_start|>", "").strip()
                
                # Remove aspas no início e fim (comum em respostas do Llama)
                if resposta.startswith('"') and resposta.endswith('"'):
                    resposta = resposta[1:-1].strip()
                if resposta.startswith("'") and resposta.endswith("'"):
                    resposta = resposta[1:-1].strip()
                
                # Remove ponto extra no final se houver ".".
                if resposta.endswith('".'):
                    resposta = resposta[:-2] + '"'
                
                # Limita a 1-2 frases
                sentences = [s.strip() for s in resposta.split('.') if s.strip()]
                if len(sentences) >= 2:
                    resposta = sentences[0] + ". " + sentences[1] + "."
                elif len(sentences) == 1:
                    resposta = sentences[0] + "."
                elif not resposta:
                    resposta = "I'm not sure how to respond to that."
                
                # 📊 EXIBE ESTATÍSTICAS DE TEMPO
                print(f"\n⏱️ TEMPO DE RESPOSTA:")
                print(f"   └─ Tempo total: {elapsed_time:.3f}s")
                print(f"   └─ Tokens/segundo: ~{len(resposta.split()) / elapsed_time:.1f} palavras/s")
                print(f"🤖 Ollama respondeu: '{resposta}'\n")
                
                return resposta
            else:
                elapsed_time = time.time() - start_time
                error_msg = result.stderr.strip() if result.stderr else "Erro desconhecido"
                print(f"❌ Erro ao executar Ollama após {elapsed_time:.2f}s:")
                print(f"   {error_msg}")
                return "I'm having trouble connecting to my brain right now."
                
        except subprocess.TimeoutExpired:
            elapsed_time = time.time() - start_time
            print(f"❌ Timeout após {elapsed_time:.2f}s")
            return "I'm thinking too slowly. Let me try again."
        except FileNotFoundError:
            print("❌ Comando 'ollama' não encontrado!")
            return "I can't access my brain right now."
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ Erro com Ollama após {elapsed_time:.2f}s: {e}")
            return "I'm having trouble thinking right now."

    def test_listening(self):
        """Teste básico de escuta"""
        print("\n🧪 TESTE DE ESCUTA")
        self.speak("Testing speech recognition. Please say hello robot.")
        
        result = self.listen(duration=5.0, extra_vocabulary=["hello", "robot"])
        
        if result:
            self.speak(f"Great! I heard: {result}")
            return True
        else:
            self.speak("I didn't hear anything. Let me check the system.")
            return False

    def run_chat(self):
        """Loop principal do chat"""
        print("\n🚀 INICIANDO CHAT NAO + OLLAMA LLAMA")
        
        # Teste inicial (opcional - comentado para iniciar mais rápido)
        # print("\n📡 Testando sistema de escuta...")
        # if not self.test_listening():
        #     print("⚠️ Problemas detectados, mas continuando...")
        
        # Saudação
        self.speak("Hello! I'm NAO with Llama AI running locally. I'm ready to chat with you in English. Please speak clearly.")
        
        conversation_count = 0
        consecutive_failures = 0
        
        while True:
            try:
                print(f"\n{'='*60}")
                print(f"--- Conversa #{conversation_count + 1} ---")
                print(f"{'='*60}")
                
                # Escuta o usuário
                print("🎤 Aguardando sua fala...")
                user_input = self.listen(duration=10.0)
                
                if user_input is None or user_input.strip() == "":
                    consecutive_failures += 1
                    print(f"❌ Falha #{consecutive_failures}")
                    
                    if consecutive_failures >= 3:
                        self.speak("I'm having trouble hearing you. Let me reset the speech system.")
                        print("🔄 Resetando sistema de fala...")
                        time.sleep(1)
                        consecutive_failures = 0
                    else:
                        feedback_messages = [
                            "I didn't catch that. Please speak louder and more clearly.",
                            "Could you repeat that? I'm listening.",
                            "Please try speaking one more time."
                        ]
                        self.speak(feedback_messages[consecutive_failures - 1])
                    continue
                
                consecutive_failures = 0
                print(f"👤 USUÁRIO DISSE: '{user_input}'")
                
                # Comandos de saída
                exit_commands = ["bye", "goodbye", "stop", "quit", "exit", "end"]
                if any(cmd in user_input.lower() for cmd in exit_commands):
                    self.speak("Goodbye! It was wonderful chatting with you. Have a great day!")
                    break
                
                # Processa com Ollama
                print("🤖 Processando com Ollama...")
                self.speak("Let me think about that.")
                
                response = self.ask_ollama(user_input)
                
                # Debug detalhado da resposta
                print(f"\n🔍 DEBUG RESPOSTA:")
                print(f"   Tipo: {type(response)}")
                print(f"   Tamanho: {len(response) if response else 0}")
                print(f"   Conteúdo: '{response}'")
                print(f"   Está vazia? {not response or not response.strip()}")
                
                # Responde
                if response and response.strip():
                    print(f"✅ Vai falar a resposta...")
                    self.speak(response)
                else:
                    print(f"❌ Resposta vazia, usando fallback")
                    self.speak("I'm not sure how to respond to that.")
                
                conversation_count += 1
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n⛔ Chat interrompido pelo usuário")
                self.speak("Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Erro no chat: {e}")
                self.speak("Sorry, I encountered an error. Let's continue.")
                time.sleep(1)

def main():
    """Função principal"""
    try:
        print("=" * 60)
        print("🤖 NAO + Ollama Llama Chat (CLI via subprocess)")
        print("=" * 60)
        
        # Configurações
        NAO_IP = "172.15.3.253"  # ALTERE PARA SEU IP
        MODEL_NAME = "llama3"     # ou "llama2", "mistral", "phi3", etc.
        
        print(f"\n📋 Configuração:")
        print(f"   NAO IP: {NAO_IP}")
        print(f"   Modelo: {MODEL_NAME}")
        print(f"\n💡 Certifique-se que Ollama está instalado:")
        print(f"   $ ollama --version")
        print(f"   $ ollama list  # para ver modelos instalados")
        print(f"   $ ollama pull {MODEL_NAME}  # se necessário\n")
        
        # Cria e executa o chat
        chat = NAOOllamaChat(NAO_IP, model_name=MODEL_NAME)
        chat.run_chat()
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        print("\n📋 Checklist:")
        print("1. ✓ NAO está ligado e conectado")
        print("2. ✓ IP do NAO está correto")
        print("3. ✓ Ollama está instalado (curl -fsSL https://ollama.com/install.sh | sh)")
        print("4. ✓ Modelo está instalado (ollama pull llama3)")
        print("5. ✓ pip install qi")

if __name__ == "__main__":
    main()
