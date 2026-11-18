"""
PROYECTO FASE 4 - PROGRAMACI0N 213023
Sistema Integral de Gesti0n de Clientes, Servicios y Reservas
Empresa simulada: Software FJ

Desarrollado con programaci0n orientada a objetos.
No utiliza bases de datos: la informaci0n se administra con objetos y listas.
Los eventos y errores se registran en el archivo sistema_logs.txt.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re



# 1. CONFIGURACI0N DEL ARCHIVO DE REGISTRO (LOGS)


logging.basicConfig(
    filename="sistema_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)



# 2. EXCEPCIONES PERSONALIZADAS


class ErrorSistema(Exception):
    """Excepción base para los errores propios del sistema."""
    pass


class DatoInvalidoError(ErrorSistema):
    """Se presenta cuando un dato ingresado no cumple las reglas."""
    pass


class ClienteNoEncontradoError(ErrorSistema):
    """Se presenta cuando no existe el cliente solicitado."""
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Se presenta cuando un servicio no está disponible."""
    pass


class ReservaNoPermitidaError(ErrorSistema):
    """Se presenta cuando una reserva no puede procesarse."""
    pass



# 3. CLASE ABSTRACTA ENTIDAD


class Entidad(ABC):
    """Representa una entidad general del sistema."""

    def __init__(self, identificador):
        if not identificador or not str(identificador).strip():
            raise DatoInvalidoError("El identificador es obligatorio.")
        self._identificador = str(identificador).strip()

    @property
    def identificador(self):
        """Permite consultar el identificador sin modificarlo directamente."""
        return self._identificador

    @abstractmethod
    def describir(self):
        """Cada clase hija debe implementar su propia descripción."""
        pass



# 4. CLASE CLIENTE


class Cliente(Entidad):
    """Almacena los datos de un cliente con encapsulación."""

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
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise DatoInvalidoError("El nombre debe tener al menos 2 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", valor.strip()
        ):
            raise DatoInvalidoError("El correo electr0nico no es valido.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        numero = re.sub(r"\s+", "", str(valor))
        if not re.fullmatch(r"\+?\d{7,15}", numero):
            raise DatoInvalidoError("El telefono debe contener entre 7 y 15 digitos.")
        self._telefono = numero

    def describir(self):
        return (
            f"Cliente: {self.nombre} | ID: {self.identificador} | "
            f"Correo: {self.correo} | Teléfono: {self.telefono}"
        )


 
# 5. CLASE ABSTRACTA SERVICIO


class Servicio(Entidad, ABC):
    """Clase base de todos los servicios ofrecidos por Software FJ."""

    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa base debe ser un numero mayor que cero.")

        self.nombre = nombre.strip()
        self.tarifa_base = float(tarifa_base)
        self.disponible = bool(disponible)

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo.
        Los parámetros opcionales permiten distintas formas de invocar
        el cálculo, simulando sobrecarga de métodos en Python.
        """
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    def describir(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.nombre} | Tarifa base: ${self.tarifa_base:,.0f} | {estado}"

    def validar_calculo(self, duracion, impuesto, descuento):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatoInvalidoError("La duración debe ser un número mayor que cero.")
        if not isinstance(impuesto, (int, float)) or not 0 <= impuesto <= 100:
            raise DatoInvalidoError("El impuesto debe estar entre 0 y 100.")
        if not isinstance(descuento, (int, float)) or not 0 <= descuento <= 100:
            raise DatoInvalidoError("El descuento debe estar entre 0 y 100.")



# 6. SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)


class ReservaSala(Servicio):
    """Servicio de reserva de salas por horas."""

    def __init__(self, identificador, nombre, tarifa_base, capacidad):
        super().__init__(identificador, nombre, tarifa_base)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError("La capacidad debe ser un entero positivo.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 1 <= duracion <= 12:
            raise DatoInvalidoError("La sala se puede reservar entre 1 y 12 horas.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        self.validar_calculo(duracion, impuesto, descuento)
        subtotal = self.tarifa_base * duracion
        return subtotal * (1 - descuento / 100) * (1 + impuesto / 100)

    def describir(self):
        return f"{super().describir()} | Capacidad: {self.capacidad} personas"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por días."""

    def __init__(self, identificador, nombre, tarifa_base, cantidad_disponible):
        super().__init__(identificador, nombre, tarifa_base)
        if not isinstance(cantidad_disponible, int) or cantidad_disponible < 0:
            raise DatoInvalidoError("La cantidad disponible no puede ser negativa.")
        self.cantidad_disponible = cantidad_disponible

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 1 <= duracion <= 30:
            raise DatoInvalidoError("El alquiler debe ser de 1 a 30 días.")
        if self.cantidad_disponible <= 0:
            raise ServicioNoDisponibleError("No hay unidades disponibles de este equipo.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        self.validar_calculo(duracion, impuesto, descuento)
        subtotal = self.tarifa_base * duracion
        return subtotal * (1 - descuento / 100) * (1 + impuesto / 100)

    def describir(self):
        return (
            f"{super().describir()} | "
            f"Unidades disponibles: {self.cantidad_disponible}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada por horas."""

    def __init__(self, identificador, nombre, tarifa_base, especialidad):
        super().__init__(identificador, nombre, tarifa_base)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatoInvalidoError("La especialidad es obligatoria.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or not 1 <= duracion <= 8:
            raise DatoInvalidoError("La asesoría debe durar entre 1 y 8 horas.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        self.validar_calculo(duracion, impuesto, descuento)
        subtotal = self.tarifa_base * duracion
        return subtotal * (1 - descuento / 100) * (1 + impuesto / 100)

    def describir(self):
        return f"{super().describir()} | Especialidad: {self.especialidad}"



# 7. CLASE RESERVA


class Reserva(Entidad):
    """Relaciona un cliente con un servicio y controla su estado."""

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva necesita un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva necesita un servicio valido.")

        servicio.validar_parametros(duracion)
        if not servicio.disponible:
            raise ServicioNoDisponibleError("El servicio no esta disponible.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.costo = 0.0

    def confirmar(self, impuesto=0, descuento=0):
        if self.estado != "Pendiente":
            raise ReservaNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        self.costo = self.servicio.calcular_costo(
            self.duracion, impuesto, descuento
        )
        self.estado = "Confirmada"

        if isinstance(self.servicio, AlquilerEquipo):
            self.servicio.cantidad_disponible -= 1

        logging.info("Reserva %s confirmada. Costo: %.2f", self.identificador, self.costo)
        return self.costo

    def cancelar(self):
        if self.estado != "Confirmada" and self.estado != "Pendiente":
            raise ReservaNoPermitidaError("La reserva no se puede cancelar.")

        if self.estado == "Confirmada" and isinstance(self.servicio, AlquilerEquipo):
            self.servicio.cantidad_disponible += 1

        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)

    def describir(self):
        return (
            f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | "
            f"Estado: {self.estado} | Costo: ${self.costo:,.0f}"
        )



# 8. CLASE PRINCIPAL PARA ADMINISTRAR EL SISTEMA


class SistemaSoftwareFJ:
    """Administra las listas de clientes, servicios y reservas."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El objeto no corresponde a un cliente.")
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatoInvalidoError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s", cliente.identificador)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El objeto no corresponde a un servicio.")
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatoInvalidoError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s", servicio.identificador)
        return servicio

    def buscar_cliente(self, identificador):
        for cliente in self.clientes:
            if cliente.identificador == str(identificador):
                return cliente
        raise ClienteNoEncontradoError(
            f"No se encontró el cliente con ID {identificador}."
        )

    def buscar_servicio(self, identificador):
        for servicio in self.servicios:
            if servicio.identificador == str(identificador):
                return servicio
        raise ServicioNoDisponibleError(
            f"No se encontró el servicio con ID {identificador}."
        )

    def crear_reserva(self, id_reserva, id_cliente, id_servicio, duracion):
        cliente = self.buscar_cliente(id_cliente)
        servicio = self.buscar_servicio(id_servicio)

        if any(r.identificador == str(id_reserva) for r in self.reservas):
            raise DatoInvalidoError("Ya existe una reserva con ese identificador.")

        reserva = Reserva(id_reserva, cliente, servicio, duracion)
        self.reservas.append(reserva)
        logging.info("Reserva creada: %s", id_reserva)
        return reserva

    def listar_clientes(self):
        if not self.clientes:
            print("No hay clientes registrados.")
            return
        for cliente in self.clientes:
            print(cliente.describir())

    def listar_servicios(self):
        if not self.servicios:
            print("No hay servicios registrados.")
            return
        for servicio in self.servicios:
            print(servicio.describir())

    def listar_reservas(self):
        if not self.reservas:
            print("No hay reservas registradas.")
            return
        for reserva in self.reservas:
            print(reserva.describir())

    def buscar_reserva(self, identificador):
        for reserva in self.reservas:
            if reserva.identificador == str(identificador):
                return reserva
        raise ReservaNoPermitidaError(
            f"No se encontró la reserva {identificador}."
        )


# 9. PRUEBAS: MÍNIMO 10 OPERACIONES COMPLETAS


def ejecutar_pruebas_demostracion():
    """
    Ejecuta más de diez operaciones para demostrar:
    registros válidos e inválidos, servicios, reservas y excepciones.
    """

    print("\n" + "=" * 65)
    print("PRUEBAS AUTOMÁTICAS DEL SISTEMA - SOFTWARE FJ")
    print("=" * 65)

    sistema = SistemaSoftwareFJ()
    contador = 0

    def resultado(titulo, accion):
        nonlocal contador
        contador += 1
        print(f"\nOPERACIÓN {contador}: {titulo}")
        try:
            accion()
            print("Resultado: operación ejecutada correctamente.")
        except (ErrorSistema, ValueError, TypeError) as error:
            logging.error("Operación %s: %s", contador, error)
            print(f"Resultado: error controlado: {error}")
        except Exception as error:
            logging.exception("Error inesperado en operación %s", contador)
            print(f"Resultado: error inesperado controlado: {error}")
        finally:
            print("Verificación finalizada.")

    # Operación 1: registrar cliente válido.
    def op1():
        sistema.registrar_cliente(
            Cliente("C001", "Ana Pérez", "ana@email.com", "3001234567")
        )
        print(sistema.clientes[-1].describir())
    resultado("Registro de cliente válido", op1)

    # Operación 2: registrar otro cliente válido.
    def op2():
        sistema.registrar_cliente(
            Cliente("C002", "Carlos Gómez", "carlos@email.com", "3107654321")
        )
        print(sistema.clientes[-1].describir())
    resultado("Registro de segundo cliente válido", op2)

    # Operación 3: intentar registrar cliente con correo inválido.
    def op3():
        cliente = Cliente("C003", "Laura Díaz", "correo_incorrecto", "3111234567")
        sistema.registrar_cliente(cliente)
    resultado("Registro de cliente con correo inválido", op3)

    # Operación 4: registrar servicio de sala.
    def op4():
        sistema.registrar_servicio(
            ReservaSala("S001", "Sala de reuniones", 50000, 12)
        )
        print(sistema.servicios[-1].describir())
    resultado("Creación de servicio de reserva de sala", op4)

    # Operación 5: registrar servicio de alquiler de equipo.
    def op5():
        sistema.registrar_servicio(
            AlquilerEquipo("S002", "Computador portátil", 80000, 3)
        )
        print(sistema.servicios[-1].describir())
    resultado("Creación de servicio de alquiler de equipos", op5)

    # Operación 6: registrar servicio de asesoría.
    def op6():
        sistema.registrar_servicio(
            AsesoriaEspecializada("S003", "Asesoría tecnológica", 60000,
                                  "Tecnología")
        )
        print(sistema.servicios[-1].describir())
    resultado("Creación de servicio de asesoría especializada", op6)

    # Operación 7: intentar crear un servicio inválido.
    def op7():
        sistema.registrar_servicio(
            ReservaSala("S004", "Sala inválida", -1000, 10)
        )
    resultado("Creación de servicio con tarifa incorrecta", op7)

    # Operación 8: crear reserva correcta.
    def op8():
        reserva = sistema.crear_reserva("R001", "C001", "S001", 2)
        print(reserva.describir())
    resultado("Creación de reserva válida", op8)

    # Operación 9: confirmar reserva.
    def op9():
        reserva = sistema.buscar_reserva("R001")
        costo = reserva.confirmar(impuesto=19, descuento=5)
        print(f"Reserva confirmada. Total: ${costo:,.0f}")
    resultado("Confirmación de reserva con impuesto y descuento", op9)

    # Operación 10: intentar crear reserva con cliente inexistente.
    def op10():
        sistema.crear_reserva("R002", "C999", "S001", 1)
    resultado("Reserva con cliente inexistente", op10)

    # Operación 11: crear y confirmar alquiler de equipo.
    def op11():
        reserva = sistema.crear_reserva("R003", "C002", "S002", 2)
        reserva.confirmar()
        print(reserva.describir())
    resultado("Reserva y confirmación de alquiler de equipo", op11)

    # Operación 12: intentar reservar equipo sin disponibilidad.
    def op12():
        equipo = sistema.buscar_servicio("S002")
        equipo.cantidad_disponible = 0
        sistema.crear_reserva("R004", "C001", "S002", 1)
    resultado("Reserva de equipo sin unidades disponibles", op12)

    # Operación 13: cancelar una reserva.
    def op13():
        reserva = sistema.buscar_reserva("R001")
        reserva.cancelar()
        print(reserva.describir())
    resultado("Cancelación de reserva", op13)

    # Operación 14: intentar calcular con duración inválida.
    def op14():
        servicio = sistema.buscar_servicio("S003")
        servicio.calcular_costo(0)
    resultado("Cálculo de costo con duración inválida", op14)

    print("\n" + "=" * 65)
    print(f"PRUEBAS FINALIZADAS: {contador} operaciones ejecutadas.")
    print("Los eventos y errores se registraron en sistema_logs.txt")
    print("=" * 65)

    return sistema



# 10. MENÚ INTERACTIVO


def solicitar_texto(mensaje):
    valor = input(mensaje).strip()
    if not valor:
        raise DatoInvalidoError("Este campo no puede quedar vacio.")
    return valor


def solicitar_numero(mensaje):
    try:
        return float(input(mensaje))
    except ValueError as error:
        # Encadenamiento de excepciones: se conserva el error original.
        raise DatoInvalidoError("Debe ingresar un valor numerico.") from error


def menu_principal(sistema):
    """Permite utilizar el sistema despues de ejecutar las pruebas."""

    while True:
        print("\n" + "=" * 55)
        print("       SISTEMA DE GESTIÓN - SOFTWARE FJ")
        print("=" * 55)
        print("1. Registrar cliente")
        print("2. Registrar servicio de sala")
        print("3. Registrar servicio de alquiler de equipo")
        print("4. Registrar servicio de asesoria")
        print("5. Crear reserva")
        print("6. Confirmar reserva")
        print("7. Cancelar reserva")
        print("8. Consultar clientes")
        print("9. Consultar servicios")
        print("10. Consultar reservas")
        print("11. Salir")

        opcion = input("Seleccione una opcion: ").strip()

        try:
            if opcion == "1":
                cliente = Cliente(
                    solicitar_texto("Identificacion: "),
                    solicitar_texto("Nombre: "),
                    solicitar_texto("Correo: "),
                    solicitar_texto("Telefono: ")
                )
                sistema.registrar_cliente(cliente)
                print("Cliente registrado correctamente.")

            elif opcion == "2":
                servicio = ReservaSala(
                    solicitar_texto("Código del servicio: "),
                    solicitar_texto("Nombre de la sala: "),
                    solicitar_numero("Tarifa por hora: "),
                    int(solicitar_numero("Capacidad de personas: "))
                )
                sistema.registrar_servicio(servicio)
                print("Servicio de sala registrado.")

            elif opcion == "3":
                servicio = AlquilerEquipo(
                    solicitar_texto("Código del servicio: "),
                    solicitar_texto("Nombre del equipo: "),
                    solicitar_numero("Tarifa por día: "),
                    int(solicitar_numero("Cantidad disponible: "))
                )
                sistema.registrar_servicio(servicio)
                print("Servicio de equipo registrado.")

            elif opcion == "4":
                servicio = AsesoriaEspecializada(
                    solicitar_texto("Codigo del servicio: "),
                    solicitar_texto("Nombre de la asesoria: "),
                    solicitar_numero("Tarifa por hora: "),
                    solicitar_texto("Especialidad: ")
                )
                sistema.registrar_servicio(servicio)
                print("Servicio de asesoria registrado.")

            elif opcion == "5":
                reserva = sistema.crear_reserva(
                    solicitar_texto("C0digo de reserva: "),
                    solicitar_texto("Identificacion del cliente: "),
                    solicitar_texto("C0digo del servicio: "),
                    solicitar_numero("Duracion (horas o dias segun servicio): ")
                )
                print("Reserva creada:", reserva.describir())

            elif opcion == "6":
                reserva = sistema.buscar_reserva(
                    solicitar_texto("Codigo de reserva: ")
                )
                impuesto = solicitar_numero("Impuesto (%) [0 si no aplica]: ")
                descuento = solicitar_numero("Descuento (%) [0 si no aplica]: ")
                total = reserva.confirmar(impuesto, descuento)
                print(f"Reserva confirmada. Total a pagar: ${total:,.0f}")

            elif opcion == "7":
                reserva = sistema.buscar_reserva(
                    solicitar_texto("Codigo de reserva: ")
                )
                reserva.cancelar()
                print("Reserva cancelada correctamente.")

            elif opcion == "8":
                sistema.listar_clientes()

            elif opcion == "9":
                sistema.listar_servicios()

            elif opcion == "10":
                sistema.listar_reservas()

            elif opcion == "11":
                print("Gracias por utilizar el sistema Software FJ.")
                logging.info("El usuario cerr0 el sistema.")
                break

            else:
                raise DatoInvalidoError("La opcion seleccionada no existe.")

        except ErrorSistema as error:
            logging.error("Error controlado en menu: %s", error)
            print(f"Atencion: {error}")

        except (ValueError, TypeError) as error:
            logging.error("Error de dato en menu: %s", error)
            print(f"Atencion: dato incorrecto. {error}")

        except Exception as error:
            logging.exception("Error inesperado en el menu.")
            print(f"Se presento un error inesperado: {error}")

        else:
            # Este bloque se ejecuta cuando la operaci0n termina sin errores.
            logging.info("Operacion del menu ejecutada correctamente.")

        finally:
            # Este bloque se ejecuta tanto si hubo error como si no.
            print("Proceso terminado. El sistema continua disponible.")



# 11. INICIO DEL PROGRAMA


def main():
    print("=" * 65)
    print("UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD")
    print("CURSO: PROGRAMACIoN 213023 - FASE 4")
    print("SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ")
    print("=" * 65)

    # Primero se ejecutan las operaciones de demostraci0n solicitadas.
    sistema = ejecutar_pruebas_demostracion()

    # Despues se permite utilizar el sistema desde el menú.
    menu_principal(sistema)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario.")
        logging.warning("El programa fue interrumpido por el usuario.")
    except Exception as error:
        logging.exception("Error critico al iniciar el programa.")
        print(f"No fue posible iniciar el programa: {error}")
    finally:
        logging.info("Finalizacion de la ejecucion.")
