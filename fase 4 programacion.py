# FASE 4 - PROGRAMACION
# SISTEMA INTEGRAL DE GESTION DE CLIENTES, SERVICIOS Y RESERVAS
# Empresa: Software FJ

#==========SECCION 1 
# IMPORTACIONES, EXCEPCIONES, ENTIDADES, CLIENTES Y SERVICIOS

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re

# Configuracion del archivo de registro de eventos y errores.
logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# Excepciones personalizadas para controlar errores del sistema.
class ErrorSistema(Exception):
    """Excepcion base del sistema."""
    pass


class DatoInvalidoError(ErrorSistema):
    """Se genera cuando un dato no cumple las validaciones."""
    pass


class ElementoNoEncontradoError(ErrorSistema):
    """Se genera cuando no existe un cliente o servicio solicitado."""
    pass


class OperacionNoPermitidaError(ErrorSistema):
    """Se genera cuando una operacion no esta permitida."""
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Se genera cuando un servicio no esta disponible."""
    pass


# Clase abstracta que representa las entidades generales.
class Entidad(ABC):
    def __init__(self, identificador):
        if not identificador or not str(identificador).strip():
            raise DatoInvalidoError("El identificador es obligatorio.")
        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def describir(self):
        pass


# Clase Cliente con encapsulacion y validaciones.
class Cliente(Entidad):
    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise DatoInvalidoError("El correo electronico no tiene un formato valido.")
        self._correo = valor.lower().strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        numero = str(valor).strip()
        if not numero.isdigit() or len(numero) < 7:
            raise DatoInvalidoError("El telefono debe contener al menos 7 digitos.")
        self._telefono = numero

    def describir(self):
        return f"Cliente: {self.nombre} | ID: {self.identificador} | Correo: {self.correo}"


# Clase abstracta Servicio. Las clases derivadas implementan sus metodos.
class Servicio(Entidad, ABC):
    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa debe ser un numero mayor que cero.")
        self.nombre = nombre.strip()
        self.tarifa_base = float(tarifa_base)
        self.disponible = bool(disponible)

    @abstractmethod
    def describir(self):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        pass


# Servicio especializado 1: reserva de salas.
class ReservaSala(Servicio):
    def describir(self):
        return f"Reserva de sala: {self.nombre}"

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0 or duracion > 12:
            raise DatoInvalidoError("La duracion de la sala debe estar entre 1 y 12 horas.")

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        return max(0, subtotal + (subtotal * impuesto) - (subtotal * descuento))


# Servicio especializado 2: alquiler de equipos.
class AlquilerEquipo(Servicio):
    def describir(self):
        return f"Alquiler de equipo: {self.nombre}"

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0 or duracion > 30:
            raise DatoInvalidoError("El alquiler debe estar entre 1 y 30 dias.")

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        return max(0, subtotal + (subtotal * impuesto) - (subtotal * descuento))


# Servicio especializado 3: asesoria especializada.
class Asesoria(Servicio):
    def describir(self):
        return f"Asesoria especializada: {self.nombre}"

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0 or duracion > 8:
            raise DatoInvalidoError("La asesoria debe estar entre 1 y 8 horas.")

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        return max(0, subtotal + (subtotal * impuesto) - (subtotal * descuento))


#====SECCION 2 
# RESERVAS Y ADMINISTRACION GENERAL DEL SISTEMA

class Reserva(Entidad):
    ESTADOS_VALIDOS = ("Pendiente", "Confirmada", "Cancelada")

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva requiere un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere un servicio valido.")
        servicio.validar_parametros(duracion)
        if not servicio.disponible:
            raise ServicioNoDisponibleError("El servicio seleccionado no esta disponible.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha_creacion = datetime.now()

    def confirmar(self):
        if self.estado != "Pendiente":
            raise OperacionNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError("El servicio ya no esta disponible.")
        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificador)
        return "Reserva confirmada correctamente."

    def cancelar(self):
        if self.estado == "Cancelada":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")
        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)
        return "Reserva cancelada correctamente."

    def procesar(self, impuesto=0.19, descuento=0.0):
        if self.estado != "Confirmada":
            raise OperacionNoPermitidaError("La reserva debe estar confirmada para procesarse.")
        if not 0 <= impuesto <= 1 or not 0 <= descuento <= 1:
            raise DatoInvalidoError("El impuesto y el descuento deben estar entre 0 y 1.")
        total = self.servicio.calcular_costo(self.duracion, impuesto, descuento)
        logging.info("Reserva %s procesada. Total: %.2f", self.identificador, total)
        return total

    def describir(self):
        return (f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Duracion: {self.duracion} | Estado: {self.estado}")


class SistemaGestion:
    def __init__(self):
        # Las listas internas reemplazan el uso de una base de datos.
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El objeto enviado no es un cliente valido.")
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise OperacionNoPermitidaError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.identificador)
        return "Cliente registrado correctamente."

    def buscar_cliente(self, identificador):
        for cliente in self.clientes:
            if cliente.identificador == str(identificador):
                return cliente
        raise ElementoNoEncontradoError("No se encontro el cliente solicitado.")

    def crear_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El objeto enviado no es un servicio valido.")
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise OperacionNoPermitidaError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logging.info("Servicio creado: %s", servicio.identificador)
        return "Servicio creado correctamente."

    def buscar_servicio(self, identificador):
        for servicio in self.servicios:
            if servicio.identificador == str(identificador):
                return servicio
        raise ElementoNoEncontradoError("No se encontro el servicio solicitado.")

    def crear_reserva(self, identificador, id_cliente, id_servicio, duracion):
        cliente = self.buscar_cliente(id_cliente)
        servicio = self.buscar_servicio(id_servicio)
        reserva = Reserva(identificador, cliente, servicio, duracion)
        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise OperacionNoPermitidaError("Ya existe una reserva con ese identificador.")
        self.reservas.append(reserva)
        logging.info("Reserva creada: %s", identificador)
        return reserva

    def listar_reservas(self):
        if not self.reservas:
            print("No hay reservas registradas.")
            return
        for reserva in self.reservas:
            print(reserva.describir())


# ======================== SECCION 3 =========================
# PRUEBAS DEL SISTEMA: MAS DE 10 OPERACIONES COMPLETAS


def ejecutar_pruebas():
    sistema = SistemaGestion()
    print("\n========== SISTEMA SOFTWARE FJ ==========")

    # Operacion 1: registrar un cliente valido.
    try:
        cliente1 = Cliente("C001", "Laura Gomez", "laura@gmail.com", "3001234567")
        print("1.", sistema.registrar_cliente(cliente1))
    except ErrorSistema as error:
        print("1. Error:", error)
        logging.error("Error al registrar cliente: %s", error)

    # Operacion 2: registrar otro cliente valido.
    try:
        cliente2 = Cliente("C002", "Carlos Ruiz", "carlos@gmail.com", "3117654321")
        print("2.", sistema.registrar_cliente(cliente2))
    except ErrorSistema as error:
        print("2. Error:", error)
        logging.error("Error al registrar cliente: %s", error)

    # Operacion 3: intentar registrar un cliente con correo invalido.
    try:
        cliente_invalido = Cliente("C003", "Ana Torres", "correo-invalido", "3101234567")
        sistema.registrar_cliente(cliente_invalido)
    except DatoInvalidoError as error:
        print("3. Registro invalido controlado:", error)
        logging.exception("Se intento registrar un cliente con datos invalidos.")

    # Operacion 4: crear un servicio de reserva de sala.
    try:
        sala = ReservaSala("S001", "Sala de reuniones", 50000)
        print("4.", sistema.crear_servicio(sala))
    except ErrorSistema as error:
        print("4. Error:", error)
        logging.error("Error al crear sala: %s", error)

    # Operacion 5: crear un servicio de alquiler de equipo.
    try:
        equipo = AlquilerEquipo("S002", "Proyector multimedia", 35000)
        print("5.", sistema.crear_servicio(equipo))
    except ErrorSistema as error:
        print("5. Error:", error)
        logging.error("Error al crear equipo: %s", error)

    # Operacion 6: crear un servicio de asesoria.
    try:
        asesoria = Asesoria("S003", "Asesoria de software", 80000)
        print("6.", sistema.crear_servicio(asesoria))
    except ErrorSistema as error:
        print("6. Error:", error)
        logging.error("Error al crear asesoria: %s", error)

    # Operacion 7: intentar crear un servicio con tarifa incorrecta.
    try:
        servicio_invalido = ReservaSala("S004", "Sala sin costo", -100)
        sistema.crear_servicio(servicio_invalido)
    except DatoInvalidoError as error:
        print("7. Servicio invalido controlado:", error)
        logging.exception("Se intento crear un servicio con tarifa invalida.")

    # Operacion 8: crear una reserva correcta.
    try:
        reserva1 = sistema.crear_reserva("R001", "C001", "S001", 2)
        print("8. Reserva creada:", reserva1.describir())
    except ErrorSistema as error:
        print("8. Error:", error)
        logging.error("Error al crear reserva: %s", error)

    # Operacion 9: confirmar la reserva.
    try:
        print("9.", reserva1.confirmar())
    except ErrorSistema as error:
        print("9. Error:", error)
        logging.error("Error al confirmar reserva: %s", error)

    # Operacion 10: procesar la reserva y calcular su costo.
    try:
        total = reserva1.procesar(impuesto=0.19, descuento=0.10)
        print(f"10. Reserva procesada. Total a pagar: ${total:,.2f}")
    except ErrorSistema as error:
        print("10. Error:", error)
        logging.error("Error al procesar reserva: %s", error)

    # Operacion 11: crear una reserva con duracion incorrecta.
    try:
        sistema.crear_reserva("R002", "C002", "S001", 20)
    except ErrorSistema as error:
        print("11. Reserva incorrecta controlada:", error)
        logging.exception("Se intento crear una reserva con duracion invalida.")

    # Operacion 12: buscar un cliente inexistente.
    try:
        sistema.buscar_cliente("C999")
    except ElementoNoEncontradoError as error:
        print("12. Busqueda controlada:", error)
        logging.exception("Busqueda de cliente inexistente.")

    # Operacion 13: crear, confirmar y cancelar otra reserva.
    try:
        reserva2 = sistema.crear_reserva("R003", "C002", "S003", 1)
        print("13. Reserva adicional:", reserva2.confirmar())
        print("    ", reserva2.cancelar())
    except ErrorSistema as error:
        print("13. Error:", error)
        logging.error("Error en la segunda reserva: %s", error)

    # Operacion 14: demostrar que no se puede procesar una reserva cancelada.
    try:
        reserva2.procesar()
    except OperacionNoPermitidaError as error:
        print("14. Procesamiento no permitido controlado:", error)
        logging.exception("Se intento procesar una reserva cancelada.")

    # Operacion 15: demostrar encadenamiento de excepciones.
    try:
        try:
            int("dato-no-numerico")
        except ValueError as error_original:
            raise DatoInvalidoError("No fue posible convertir el dato a numero.") from error_original
    except DatoInvalidoError as error:
        print("15. Excepcion encadenada controlada:", error)
        logging.exception("Error de conversion de datos.")

    # Ejemplo de try/except/else/finally.
    print("\n--- Verificacion adicional ---")
    try:
        cantidad = len(sistema.reservas)
    except Exception as error:
        print("No se pudo consultar la cantidad de reservas:", error)
        logging.exception("Error al consultar reservas.")
    else:
        print("Cantidad total de reservas registradas:", cantidad)
    finally:
        print("La verificacion finalizo. El sistema continua activo.")
        logging.info("Finalizacion de las pruebas del sistema.")

    print("\n--- Listado final de reservas ---")
    sistema.listar_reservas()
    print("\nPruebas finalizadas. Consulte el archivo logs.txt para revisar los eventos.")


if __name__ == "__main__":
    ejecutar_pruebas()
