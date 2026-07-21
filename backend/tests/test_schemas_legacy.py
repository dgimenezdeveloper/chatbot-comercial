"""Tests para schemas legacy (admin, catalog, calendar, faq, chat)."""

import pytest
from pydantic import ValidationError

from app.schemas.admin import NegocioRequest, NegocioResponse
from app.schemas.calendar import TurnoRequest, TurnoResponse
from app.schemas.catalog import ProductoRequest, ProductoResponse, ServicioRequest, ServicioResponse
from app.schemas.chat import MensajeRequest, MensajeResponse
from app.schemas.faq import FAQRequest, FAQResponse


# ============================================================================
# Admin schemas
# ============================================================================

class TestNegocioRequest:
    def test_valid(self):
        n = NegocioRequest(
            nombre="Salon Test",
            descripcion="Un salon de pruebas",
            horarios="L-V 9-20",
            contacto="5491112345678",
        )
        assert n.nombre == "Salon Test"

    def test_missing_nombre_raises(self):
        with pytest.raises(ValidationError):
            NegocioRequest(descripcion="x", horarios="x", contacto="x")  # type: ignore[arg-type]

    def test_model_config_from_attributes(self):
        assert NegocioRequest.model_config.get("from_attributes") is True


class TestNegocioResponse:
    def test_valid(self):
        n = NegocioResponse(
            id=1, nombre="Salon", descripcion="x", horarios="x", contacto="x",
        )
        assert n.id == 1

    def test_model_config_from_attributes(self):
        assert NegocioResponse.model_config.get("from_attributes") is True


# ============================================================================
# Catalog schemas (Servicio)
# ============================================================================

class TestServicioRequest:
    def test_valid(self):
        s = ServicioRequest(nombre="Corte", descripcion="Corte clasico", duracion_minutos=30, precio=5000.0)
        assert s.nombre == "Corte"
        assert s.duracion_minutos == 30

    def test_descripcion_optional(self):
        s = ServicioRequest(nombre="Corte", duracion_minutos=30, precio=5000.0)
        assert s.descripcion is None

    def test_model_config_from_attributes(self):
        assert ServicioRequest.model_config.get("from_attributes") is True


class TestServicioResponse:
    def test_valid(self):
        s = ServicioResponse(id=1, nombre="Corte", duracion_minutos=30, precio=5000.0)
        assert s.id == 1

    def test_model_config_from_attributes(self):
        assert ServicioResponse.model_config.get("from_attributes") is True


# ============================================================================
# Catalog schemas (Producto)
# ============================================================================

class TestProductoRequest:
    def test_valid(self):
        p = ProductoRequest(nombre="Shampoo", precio=3500.0, stock=20, activo=True)
        assert p.nombre == "Shampoo"
        assert p.activo is True

    def test_activo_default(self):
        p = ProductoRequest(nombre="Shampoo", precio=3500.0, stock=20)
        assert p.activo is True

    def test_model_config_from_attributes(self):
        assert ProductoRequest.model_config.get("from_attributes") is True


class TestProductoResponse:
    def test_valid(self):
        p = ProductoResponse(id=1, nombre="Shampoo", precio=3500.0, stock=20, activo=True)
        assert p.id == 1

    def test_model_config_from_attributes(self):
        assert ProductoResponse.model_config.get("from_attributes") is True


# ============================================================================
# Calendar schemas
# ============================================================================

class TestTurnoRequest:
    def test_valid(self):
        t = TurnoRequest(telefono="5491112345678", servicio_id=1, fecha="2026-01-01", hora="10:00")
        assert t.telefono == "5491112345678"

    def test_model_config_from_attributes(self):
        assert TurnoRequest.model_config.get("from_attributes") is True


class TestTurnoResponse:
    def test_valid(self):
        t = TurnoResponse(id=1, telefono="5491112345678", servicio_id=1, fecha="2026-01-01", hora="10:00")
        assert t.estado == "confirmado"

    def test_model_config_from_attributes(self):
        assert TurnoResponse.model_config.get("from_attributes") is True


# ============================================================================
# FAQ schemas
# ============================================================================

class TestFAQRequest:
    def test_valid(self):
        f = FAQRequest(pregunta="¿Precio?", respuesta="$5000")
        assert f.pregunta == "¿Precio?"

    def test_model_config_from_attributes(self):
        assert FAQRequest.model_config.get("from_attributes") is True


class TestFAQResponse:
    def test_valid(self):
        f = FAQResponse(id=1, pregunta="¿Precio?", respuesta="$5000")
        assert f.id == 1

    def test_model_config_from_attributes(self):
        assert FAQResponse.model_config.get("from_attributes") is True


# ============================================================================
# Chat schemas
# ============================================================================

class TestMensajeRequest:
    def test_valid(self):
        m = MensajeRequest(telefono="5491112345678", mensaje="Hola")
        assert m.telefono == "5491112345678"
        assert m.mensaje == "Hola"

    def test_model_config_from_attributes(self):
        assert MensajeRequest.model_config.get("from_attributes") is True


class TestMensajeResponse:
    def test_valid(self):
        m = MensajeResponse(respuesta="Hola, ¿en qué te ayudo?", tipo="text")
        assert m.respuesta == "Hola, ¿en qué te ayudo?"
        assert m.tipo == "text"

    def test_tipo_default(self):
        m = MensajeResponse(respuesta="Hola")
        assert m.tipo == "text"

    def test_model_config_from_attributes(self):
        assert MensajeResponse.model_config.get("from_attributes") is True
