# 🌐 Importação dos módulos essenciais da API
# 🌐 Import essential API modules
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# 🔐 Carrega variáveis de ambiente do arquivo .env (ex: chave da IA)
# 🔐 Load environment variables from .env (e.g. AI API key)
load_dotenv()

# 📦 Importação dos módulos internos do projeto
# 📦 Import internal project modules
from .database import create_db_and_tables, get_session, engine
from .models import Product, Transaction
from .services.ai_parser import parse_user_message, UserIntent, PurchaseIntent, UnknownIntent

# 🚀 Criação da instância FastAPI com metadados de documentação
# 🚀 Create FastAPI instance with documentation metadata
app = FastAPI(
    title="🧃 HappyLoop Soda Machine API",
    description="API inteligente para simular compras de refrigerantes usando linguagem natural e IA.",
    version="1.0.0"
)

# 🧱 Evento executado na inicialização da API
# 🧱 Event executed on API startup
@app.on_event("startup")
def startup():
    create_db_and_tables()
    with Session(engine) as session:
        # 🔍 Se ainda não houver produtos, adiciona os iniciais
        # 🔍 If no products exist yet, add initial items
        if not session.exec(select(Product)).first():
            session.add_all([
                Product(name="Coca-Cola", price=2.50, stock=100),
                Product(name="Pepsi", price=2.20, stock=80),
                Product(name="Guaraná", price=2.00, stock=120)
            ])
            session.commit()

# 🏠 Endpoint raiz: exibe mensagem de boas-vindas na API
# 🏠 Root endpoint: displays welcome message in the API
@app.get("/", tags=["Sistema"])
def root():
    return {"message": "Bem-vindo à HappyLoop Soda Machine API! Acesse /docs para a documentação interativa."}

# 💬 Interface visual HTML para interação via navegador
# 💬 HTML visual interface for browser interaction
@app.get("/interface", response_class=HTMLResponse, tags=["Interface"])
def interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>🧃 HappyLoop Interação</title>
    </head>
    <body style='font-family:sans-serif; max-width:600px; margin:auto; padding:2rem;'>
        <h1>🧃 HappyLoop Soda Machine</h1>
        <p>Digite sua mensagem em linguagem natural (ex: "Quero comprar 3 Coca-Cola"):</p>
        <input type="text" id="msg" placeholder="Ex: Quero comprar 2 Guaraná" style="width:100%; padding:8px;" />
        <button onclick="enviar()" style="margin-top:10px; padding:8px 16px;">🛒 Enviar</button>
        <pre id="resposta" style="background:#f4f4f4; padding:1rem; margin-top:2rem;"></pre>
        <script>
            // 📨 Envia a mensagem como JSON para o backend
            // 📨 Sends the message as JSON to the backend
            async function enviar() {
                const msg = document.getElementById("msg").value;
                const res = document.getElementById("resposta");
                const r = await fetch("/interact/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: msg })
                });
                const data = await r.json();
                res.textContent = JSON.stringify(data, null, 2);
            }
        </script>
        <hr/>
        <a href="/docs" target="_blank">🔍 Ver documentação Swagger</a>
    </body>
    </html>
    """

# 🧃 Endpoint para listar todos os produtos cadastrados
# 🧃 Endpoint to list all registered products
@app.get("/products/", response_model=list[Product], tags=["Produtos"])
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()

# 🧾 Endpoint para listar todas as transações realizadas
# 🧾 Endpoint to list all recorded transactions
@app.get("/transactions/", response_model=list[Transaction], tags=["Transações"])
def list_transactions(session: Session = Depends(get_session)):
    return session.exec(select(Transaction)).all()

# 📥 Modelo de entrada contendo a mensagem do usuário
# 📥 Input model containing the user's message
class UserInputMessage(BaseModel):
    message: str = Field(..., example="Quero comprar 3 Coca-Cola")

# 🧠 Endpoint principal que interpreta a mensagem e executa a compra
# 🧠 Main endpoint that interprets the message and executes the purchase
@app.post("/interact/", tags=["Interações"])
def interact(user_input: UserInputMessage, session: Session = Depends(get_session)):
    intent = parse_user_message(user_input.message)

    # 🛒 Se a IA identificar intenção de compra, processa o pedido
    # 🛒 If AI identifies a purchase intent, process the request
    if intent.type == "purchase" and isinstance(intent.data, PurchaseIntent):
        name = intent.data.product_name.strip()
        quantity = intent.data.quantity

        # ⚠️ Verifica se a quantidade é válida
        # ⚠️ Check if quantity is valid
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="A quantidade deve ser positiva.")

        # 🔍 Procura pelo produto no banco de dados (case-insensitive)
        # 🔍 Look up product in the database (case-insensitive)
        product = session.exec(select(Product).where(Product.name.ilike(name))).first()

        # 🔄 Se não encontrar exatamente, tenta por similaridade
        # 🔄 If exact match not found, try similarity search
        if not product:
            for p_name in session.exec(select(Product.name)).all():
                if name.lower() in p_name.lower():
                    product = session.exec(select(Product).where(Product.name == p_name)).first()
                    break
            if not product:
                raise HTTPException(status_code=404, detail=f"Produto '{name}' não encontrado.")

        # 📉 Verifica se há estoque suficiente
        # 📉 Check if there's enough stock
        if product.stock < quantity:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente. Disponível: {product.stock}")

        # ✍️ Atualiza o estoque e registra a transação
        # ✍️ Update stock and record the transaction
        product.stock -= quantity
        total = product.price * quantity
        transaction = Transaction(product_id=product.id, quantity=quantity, total_price=total)

        session.add_all([product, transaction])
        session.commit()

        # ✅ Retorna os dados da compra concluída
        # ✅ Return data for the successful purchase
        return {
            "status": "success",
            "message": f"Compra realizada: {quantity} x {product.name} por R${total:.2f}.",
            "stock_restante": product.stock,
            "product": product.model_dump(),
            "transaction": transaction.model_dump()
        }

    # ❓ Se a intenção não for reconhecida pela IA, retorna erro
    # ❓ If AI does not recognize the intent, return error
    elif intent.type == "unknown" and isinstance(intent.data, UnknownIntent):
        raise HTTPException(status_code=400, detail=f"Intenção não compreendida: {intent.data.reason}")

    # 🚨 Caso algo inesperado ocorra, retorna erro interno
    # 🚨 If something unexpected happens, return internal error
    raise HTTPException(status_code=500, detail="Erro inesperado ao interpretar a mensagem.")