import os
import sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(os.path.dirname(parent))

import config
from core.redfishConfig import RedfishConfig

import atheris

with atheris.instrument_imports():
    from core.redfishCommand import RedfishCommand

def TestOneInput(inputBytes):
    fdp = atheris.FuzzedDataProvider(inputBytes)
    # fuzzedData = fdp.ConsumeUnicode(sys.maxsize)
    fuzzedData = fdp.ConsumeUnicodeNoSurrogates(sys.maxsize)

    redfishConfig = RedfishConfig(config.defaultConfigFile)
    RedfishCommand.execute(redfishConfig, fuzzedData)

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
