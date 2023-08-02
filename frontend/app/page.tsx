'use client'

import { useCallback, useEffect, useState, Suspense, lazy } from 'react';
import { RadioGroup } from '@headlessui/react'
let MyPlot = lazy(() => import("../components/plot"));

// Define types
type Typ = 'comments' | 'logs';
type Extension = '*' | 'py' | 'java';
type State = Record<Typ, Record<Extension, string>>;

// Enumerate for iteration
const ALL_TYPS: Typ[] = ['comments', 'logs'];
const ALL_EXTENSIONS: Extension[] = ['*', 'py', 'java'];

async function fetchData() {
  const raw = await fetch("http://localhost:3001/get_graphs");
  return await raw.json() as State;
}

async function refreshBackend() {
  await fetch("http://localhost:3001/refresh", { method: "POST" });
}

export default function Home() {
  const [state, setState] = useState<State | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [typ, setTyp] = useState<Typ>("comments");
  const [ext, setExt] = useState<Extension>("*");
  const [arePlotsLoading, setArePlotsLoading] = useState(true);
  const dataObj = state !== null ? JSON.parse(state[typ][ext]) : null;

  const doRefresh = useCallback(async (hard = false) => {
    setIsLoading(true);
    if (hard) {
      await refreshBackend();
    }
    setArePlotsLoading(true);
    const data = await fetchData();
    setIsLoading(false);
    setState(data);
  }, [])

  useEffect(() => {
    doRefresh();
  }, []);


  return (
    <main className="flex min-h-screen w-screen p-8 overflow-x-clip">
      <div className="flex flex-col basis-1/6">
        <div className="flex justify-center mb-8">
          <img src="Nutanix-Era-40.svg" />
          <p className="font-bold font-sans ml-4 text-2xl">NDB Code Viz</p>
        </div>
        <div>
          <p className="italic text-lg mb-4">What do you want to analyze?</p>
          <RadioGroup value={typ} onChange={setTyp} className="px-2">
            <RadioGroup.Label className="sr-only">Server size</RadioGroup.Label>
            <div className="space-y-2">
              {ALL_TYPS.map((atyp) => (
                <RadioGroup.Option
                  key={atyp}
                  value={atyp}
                  className={({ active, checked }) =>
                    `${active
                      ? 'ring-2 ring-white ring-opacity-60 ring-offset-2 ring-offset-sky-300'
                      : ''
                    }
                  ${checked ? 'bg-sky-900 bg-opacity-75 text-white' : 'bg-white'
                    }
                    relative flex cursor-pointer rounded-lg px-5 py-4 shadow-md focus:outline-none`
                  }
                >
                  {({ checked }) => (
                    <>
                      <div className="flex w-full items-center justify-between">
                        <div className="flex items-center">
                          <div className="text-sm">
                            <RadioGroup.Label
                              as="p"
                              className={`font-medium  ${checked ? 'text-white' : 'text-gray-900'
                                }`}
                            >
                              {atyp}
                            </RadioGroup.Label>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </RadioGroup.Option>
              ))}
            </div>
          </RadioGroup>
          <p className="italic text-lg mt-8 mb-4">On what kind of files?</p>
          <RadioGroup value={ext} onChange={setExt} className="px-2">
            <RadioGroup.Label className="sr-only">Server size</RadioGroup.Label>
            <div className="space-y-2">
              {ALL_EXTENSIONS.map((aext) => (
                <RadioGroup.Option
                  key={aext}
                  value={aext}
                  className={({ active, checked }) =>
                    `${active
                      ? 'ring-2 ring-white ring-opacity-60 ring-offset-2 ring-offset-sky-300'
                      : ''
                    }
                  ${checked ? 'bg-sky-900 bg-opacity-75 text-white' : 'bg-white'
                    }
                    relative flex cursor-pointer rounded-lg px-5 py-4 shadow-md focus:outline-none`
                  }
                >
                  {({ checked }) => (
                    <>
                      <div className="flex w-full items-center justify-between">
                        <div className="flex items-center">
                          <div className="text-sm">
                            <RadioGroup.Label
                              as="p"
                              className={`font-medium  ${checked ? 'text-white' : 'text-gray-900'
                                }`}
                            >
                              .{aext}
                            </RadioGroup.Label>
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </RadioGroup.Option>
              ))}
            </div>
          </RadioGroup>
        </div>
        <button className={`hover:cursor-pointer p-4 mt-8 rounded-full ${isLoading ? "bg-sky-100" : "bg-sky-400"}`} disabled={isLoading} onClick={() => {
          if (!isLoading) doRefresh(true);
        }}>
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>
      {dataObj && <div className="flex basis-4/5">
        <div className={`w-full h-full`} key={`${typ}-${ext}`}>
          <MyPlot
            data={dataObj["data"]}
            layout={dataObj["layout"]}
            className="w-full h-full"
            style={{ width: "100%", height: "100%" }}
            useResizeHandler
            onAfterPlot={() => setArePlotsLoading(false)}
            setArePlotsLoading={setArePlotsLoading}
            dataObj={dataObj}
          />
        </div>
      </div>}
    </main >
  )
}
