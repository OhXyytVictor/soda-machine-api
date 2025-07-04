# 🔧 Tipos opcionais e relacionamentos dinâmicos
# 🔧 Optional types and dynamic relationships
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

# 🧃 Modelo que representa um produto (refrigerante) disponível para venda
# 🧃 Model representing a soda product available for sale
class Product(SQLModel, table=True):
    # 🆔 Identificador único do produto (gerado automaticamente)
    # 🆔 Unique product ID (automatically generated)
    id: Optional[int] = Field(default=None, primary_key=True)

    # 🧾 Nome do produto (indexado e único)
    # 🧾 Product name (indexed and unique)
    name: str = Field(
        index=True,
        unique=True,
        description="Nome do refrigerante (e.g., 'Coca-Cola', 'Guaraná')"  # BR
        # "Name of the soda (e.g., 'Coca-Cola', 'Guaraná')"               # EN
    )

    # 💲 Preço por unidade
    # 💲 Unit price
    price: float = Field(description="Preço unitário do refrigerante")  # BR
    # price: float = Field(description="Unit price of the soda")        # EN

    # 📦 Quantidade disponível em estoque (não pode ser negativa)
    # 📦 Available stock quantity (cannot be negative)
    stock: int = Field(ge=0, description="Nível de estoque atual do refrigerante")  # BR
    # stock: int = Field(ge=0, description="Current inventory level")               # EN

    # 🔄 (Opcional) Relacionamento reverso com transações
    # 🔄 (Optional) Reverse relationship with transactions
    # transactions: list["Transaction"] = Relationship(back_populates="product")

# 💳 Modelo que representa uma transação de compra realizada
# 💳 Model representing a completed purchase transaction
class Transaction(SQLModel, table=True):
    # 🆔 Identificador único da transação
    # 🆔 Unique transaction ID
    id: Optional[int] = Field(default=None, primary_key=True)

    # 🔗 Chave estrangeira vinculada ao produto comprado
    # 🔗 Foreign key linked to purchased product
    product_id: int = Field(
        foreign_key="product.id",
        description="ID do produto de refrigerante comprado"  # BR
        # description="ID of the purchased soda product"       # EN
    )

    # 🔢 Quantidade comprada (deve ser maior que 0)
    # 🔢 Quantity purchased (must be greater than 0)
    quantity: int = Field(gt=0, description="Quantidade comprada")  # BR
    # quantity: int = Field(gt=0, description="Amount purchased")   # EN

    # 💰 Valor total da transação (preço unitário × quantidade)
    # 💰 Total transaction amount (unit price × quantity)
    total_price: float = Field(description="Preço total da transação")  # BR
    # total_price: float = Field(description="Total transaction price") # EN

    # 🕒 Data e hora em que a compra foi realizada
    # 🕒 Date and time when the purchase was made
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Data e hora da transação"  # BR
        # description="Timestamp of the transaction" # EN
    )

    # 🔄 (Opcional) Relacionamento reverso com o produto
    # 🔄 (Optional) Reverse relationship with the product
    # product: Product = Relationship(back_populates="transactions")