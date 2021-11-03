import asyncio
import os
import time
from random import randint
from typing import Optional

import aiohttp
import requests
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)

app = FastAPI()

tracer_provider = TracerProvider(resource=Resource.create({
        "service.name": os.environ.get("HOSTNAME")
    }))

trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer_provider().get_tracer(__name__)

# create a JaegerExporter
jaeger_exporter = JaegerExporter(
    agent_host_name='jaeger',
    agent_port=6831,
)

# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

trace.get_tracer_provider().add_span_processor(span_processor)

@app.get("/async")
async def async_request(host: Optional[str] = "localhost", send_delay: Optional[int] = 0, response_delay: Optional[int] = 0):
    params = {'response_delay': response_delay}
    await asyncio.sleep(send_delay)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{host}", params=params) as response:
            return await response.text()

@app.get("/sync")
def sync_request(host: Optional[str] = "localhost", send_delay: Optional[int] = 0, response_delay: Optional[int] = 0):
    params = {'response_delay': response_delay}
    time.sleep(send_delay)
    return requests.get(f"http://{host}", params=params).text

@app.get("/")
def random_value(response_delay: Optional[int] = 0):

    time.sleep(response_delay)
    return randint(0,100)

RequestsInstrumentor().instrument()
FastAPIInstrumentor.instrument_app(app)
