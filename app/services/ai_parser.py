# 📦 Importações padrão para manipulação de ambiente e dados
# 📦 Standard imports for environment and data handling
import os
import json
import re

# 🔍 Validação de dados com Pydantic
# 🔍 Data validation with Pydantic
from pydantic import BaseModel, Field, ValidationError

# 🧠 Tipagem dinâmica e composição de tipos
# 🧠 Dynamic typing and type composition
from typing import Optional, Union

# 🤖 Integração com a API da Gemini (IA generativa do Google)
# 🤖 Integration with Gemini API (Google's generative AI)
import google.generativeai as genai

# 🔐 Configura a chave de autenticação da Gemini via variáveis de ambiente
# 🔐 Set Gemini API authentication using environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🧠 Cria uma instância do modelo generativo desejado
# 🧠 Create an instance of the desired generative model
model = genai.GenerativeModel("gemini-2.0-flash")  # ou "gemini-1.5-pro" / or "gemini-1.5-pro"

# ------------------------------------------------------------------
# 📄 Modelos Pydantic para representar a intenção do usuário
# 📄 Pydantic schemas to represent user intent
# ------------------------------------------------------------------

class PurchaseIntent(BaseModel):
    # 🧃 Nome do produto que o usuário deseja comprar
    # 🧃 Name of the soda product the user wants to purchase
    product_name: str = Field(description="Nome do refrigerante (ex: Coca-Cola).")

    # 🔢 Quantidade solicitada (deve ser número inteiro positivo)
    # 🔢 Quantity requested (must be a positive integer)
    quantity: int = Field(description="Quantidade comprada (inteiro positivo).")

class UnknownIntent(BaseModel):
    # ❓ Explicação do motivo pelo qual a IA não entendeu a intenção
    # ❓ Reason why the AI couldn't identify the intent
    reason: str = Field(description="Motivo pelo qual a intenção não pôde ser determinada.")

class UserIntent(BaseModel):
    # 🎯 Tipo de intenção identificada: 'purchase' ou 'unknown'
    # 🎯 Type of detected intent: 'purchase' or 'unknown'
    type: str = Field(description="Tipo de intenção: 'purchase' ou 'unknown'.", examples=["purchase", "unknown"])

    # 📦 Dados relacionados à intenção (modelo dependente)
    # 📦 Related intent data (dependent schema)
    data: Optional[Union[PurchaseIntent, UnknownIntent]] = Field(description="Dados associados à intenção.")

# ------------------------------------------------------------------
# 🔍 Função principal que interpreta a frase do usuário com IA
# 🔍 Main function that interprets user's sentence using AI
# ------------------------------------------------------------------

def parse_user_message(message: str) -> UserIntent:
    try:
        # 🧠 Envia instruções para o modelo generativo interpretar a frase
        # 🧠 Send prompt to generative model to interpret the sentence
        response = model.generate_content(
            f"""
            Você é o assistente de uma máquina de refrigerantes.
            Interprete a frase do usuário e retorne APENAS um JSON.

            ✅ Se for uma compra:
            {{
              "type": "purchase",
              "data": {{
                "product_name": "Coca-Cola",
                "quantity": 3
              }}
            }}

            ❌ Se a frase for ambígua ou incompleta:
            {{
              "type": "unknown",
              "data": {{
                "reason": "Texto ambíguo ou incompleto"
              }}
            }}

            Frase: "{message}"
            """
        )

        # 🕵️‍♂️ Extrai o JSON da resposta textual usando expressão regular
        # 🕵️‍♂️ Extract JSON from the text response using regex
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        parsed_json = json.loads(match.group()) if match else {}

        # 🔄 Converte o JSON em uma instância Pydantic
        # 🔄 Convert JSON into Pydantic instance
        return UserIntent(**parsed_json)

    # ⚠️ Caso a estrutura do JSON seja inválida, retorna como "unknown"
    # ⚠️ If JSON structure is invalid, return as "unknown"
    except ValidationError as e:
        return UserIntent(
            type="unknown",
            data=UnknownIntent(reason=f"Erro de validação: {e}")
        )

    # 🚨 Captura quaisquer erros inesperados da Gemini e os devolve como erro IA
    # 🚨 Catch any unexpected Gemini errors and return as AI error
    except Exception as e:
        return UserIntent(
            type="unknown",
            data=UnknownIntent(reason=f"Erro com Gemini: {type(e).__name__}: {e}")
        )