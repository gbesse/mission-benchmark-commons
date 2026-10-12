# Mission Benchmark Commons

[![CI](https://github.com/gbesse/mission-benchmark-commons/actions/workflows/ci.yml/badge.svg)](https://github.com/gbesse/mission-benchmark-commons/actions) · [![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE) · FR / EN / ES

[Français](README.md) · [English](README.en.md) · Español

Comparar la precisión de dos motores orbitales.

Basilisk RK4 y Orekit KeplerianPropagator comparten estados iniciales ISS/SGP4 o Luna/JPL DE440s. Inspeccionar diferencias numéricas, deriva de energía y residuos del modelo.

![Mission Benchmark Commons](docs/mission-benchmark-commons-es.png)

## Probar en un minuto

La demo usa cálculos reales archivados e incluidos en este repositorio autónomo. Node.js 22+ basta; no se necesita cuenta, clave API, repositorio padre ni servicio externo para reproducir.

```sh
git clone https://github.com/gbesse/mission-benchmark-commons.git
cd mission-benchmark-commons
node bin/cli.js demo --locale=es
npm start
```

http://127.0.0.1:4323/?lang=es

Interfaz local FR/EN/ES, desafío diario UTC de un catálogo fijo, predicción evaluada, URL reproducible de parámetros, prueba JSON y tarjeta PNG. Historial local; sin clasificación global ni tráfico inventado.

## Ejecutar motores reales

Python 3.11–3.13 y curl; Java 17+ en Linux, JDK descargado en macOS ARM.

Basilisk 2.12.0 · Orekit 13.1.9 · SGP4 2.25 · SpiceyPy 8.2.0

```sh
npm run setup:engines
npm run test:engines
node bin/cli.js run --locale=es
```

El botón «Ejecutar» y el comando `run` inician motores instalados; «Reproducir» no inicia ningún motor. Sin sustitución sintética. La instalación descarga solo dependencias del proyecto en `.local/space-runtime`, ignorado por Git. `SPACE_RUNTIME` puede indicar un runtime existente; `SPACE_LOCALE` selecciona idioma de instalación.

## Método, datos y límites

Basilisk RK4 y Orekit KeplerianPropagator comparten el estado inicial, la gravedad y ejes inerciales fijos. El residuo SGP4/JPL también mide las limitaciones del modelo de dos cuerpos. Este benchmark no certifica software de vuelo.

Se incluyen versiones, parámetros, huellas y avisos. No se redistribuyen archivos H5/SPK ni binarios; sus fuentes y SHA-256 están fijados. Dependencias y datos externos mantienen sus condiciones.

Proyecto de software independiente MIT, sin afiliación con NASA/JPL, ESA ni proveedores citados. No necesita software ni API de máquinas de fabricación. Código extraído de Frontier Lab y adaptado a repositorio autónomo; procedencia en `upstream.json`. No se traducen datos del usuario. Las exportaciones CLI no sobrescriben archivos.

## Verificar y contribuir

```sh
npm ci
npm test
npx playwright install chromium
npm run test:browser
npm run format:check
```

`npm run build` exporta `output/site` para alojamiento estático en la raíz de un dominio. Esta edición reproduce casos publicados, sin exponer motores ni API locales.

[Mission Benchmark Commons](https://github.com/gbesse/mission-benchmark-commons) · [Contact Market](https://github.com/gbesse/contact-market) · [Citizen Mission](https://github.com/gbesse/citizen-mission)
