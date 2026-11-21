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
