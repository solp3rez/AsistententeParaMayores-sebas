// Procesa recordatorios para CERCA-001.
// "procesado" no confirma entrega ni reproducción.
routerAdd('POST', '/api/cerca/programados/procesar', (e) => {
  const datos = new DynamicModel({ iniciar: false, inicio: 0 })
  e.bindBody(datos)

  const ahora = Date.now()
  if (datos.iniciar) return e.json(200, { inicio: ahora })

  const inicio = Number(datos.inicio)
  if (!Number.isFinite(inicio) || inicio <= 0 || inicio > ahora) {
    throw new BadRequestError('Inicio inválido.')
  }

  const minuto = Math.floor(ahora / 60000) * 60000

  // No enviar recordatorios cuya hora pasó antes de iniciar.
  if (minuto <= inicio) return e.json(200, { items: [] })

  // Horario de Argentina: UTC-3.
  const local = new Date(ahora - 3 * 60 * 60 * 1000).toISOString()
  const fecha = local.slice(0, 10)
  const hora = local.slice(11, 16)
  const salida = []

  $app.runInTransaction((tx) => {
    let parlante
    try {
      parlante = tx.findFirstRecordByFilter(
        'parlantes',
        'identificador = {:identificador}',
        { identificador: 'CERCA-001' }
      )
    } catch (_) {
      return
    }

    if (!parlante.getBool('activo')) return

    const familiar = parlante.getString('familiar')
    const persona = parlante.getString('persona_mayor')
    if (!familiar || !persona) return

    try {
      if (tx.findRecordById('personas_mayores', persona).getString('familiar') !== familiar) return
    } catch (_) {
      return
    }

    const registros = tx.findRecordsByFilter(
      'mensajes_programados',
      'date = {:fecha} && time = {:hora} && repeat = "once" && estado = "pendiente" && familiar = {:familiar} && persona_mayor = {:persona}',
      'created,id', 20, 0,
      { fecha, hora, familiar, persona }
    )

    for (const registro of registros) {
      const creado = Date.parse(registro.getString('created').replace(' ', 'T'))
      const texto = registro.getString('message').trim()

      if (!Number.isFinite(creado) || creado > minuto ||
          !texto || texto.length > 200 ||
          registro.getString('mode') !== 'text' ||
          registro.getString('texto').trim() !== texto) continue

      registro.set('estado', 'procesado')
      tx.save(registro)
      salida.push({ id: registro.id, texto })
    }
  })

  return e.json(200, { items: salida })
}, $apis.requireAuth('servicio_alertas'))
