from datetime import datetime, timedelta

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.voos_model import Voo

voos_router = APIRouter(prefix="/voos")


@voos_router.get("/vendas")
def get_voos_vendas():
    with get_session() as session:
        LIMITE_HORAS = 2
        hora_atual = datetime.now()
        hora_limite = hora_atual + timedelta(hours=LIMITE_HORAS)
        voos = session.query(Voo).filter(Voo.data_saida >= hora_limite).all()
        return JSONResponse(content=voos)

@voos_router.get("/vendas")
def lista_voos_venda():
    LIMITE_HORAS = 3
    with get_session() as session:
        hora_limite = datetime.now() + timedelta(hours=LIMITE_HORAS)
        statement = select(Voo).where(Voo.data_saida >= hora_limite)
        voo = session.exec(statement).all()
        return voo


@voos_router.get("")
def lista_voos():
    with get_session() as session:
        statement = select(Voo)
        voo = session.exec(statement).all()
        return voo

# TODO - Implementar rota que retorne as poltronas por id do voo

@voos_router.post("/reservas")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        voo = session.get(Voo, reserva.voo_id)
        reservas = session.query(Reserva).filter(Reserva.documento == reserva.documento).all()
        if reservas:
            raise HTTPException(status_code=400, detail="Já existe uma reserva com este número de documento")
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva

@voos_router.post("/reserva/:codigo_reserva/checkin/:num_poltrona")
def faz_checkin(codigo_reserva: str, num_poltrona: str):
    with get_session() as session:
        reserva = session.get(Reserva, codigo_reserva)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")
        if reserva.poltrona != None:
            raise HTTPException(status_code=400, detail="Poltrona já ocupada")
        if reserva.voo.data_saida <= datetime.now():
            raise HTTPException(status_code=400, detail="Voo já saiu")
        reserva.poltrona = num_poltrona
        session.commit()
        return reserva

@voos_router.patch("/reserva/:codigo_reserva/checkin/:num_poltrona")
def faz_checkin(codigo_reserva: str, num_poltrona: str):
    with get_session() as session:
        reserva = session.get(Reserva, codigo_reserva)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva não encontrada")
        voo = session.get(Voo, reserva.voo_id)
        poltronas_ocupadas = voo.poltronas.filter(Reserva.poltrona != None).all()
        if num_poltrona in [poltrona.numero for poltrona in poltronas_ocupadas]:
            raise HTTPException(status_code=400, detail="Poltrona já ocupada")
        reserva.poltrona = num_poltrona
        session.commit()
        return reserva 