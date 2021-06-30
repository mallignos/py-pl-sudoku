#import os
#import sys
import json
import subprocess
from typing import Optional,Any,Union


class SicstusCommunicator:
    #proc : subprocess.Popen[str]

    _idcounter : int = 0

    def __init__(self,
        consultFile : Union[None,str,list[str]] = None,
        exe_path : str = 'sicstus',
        pl_path : str = '$SP_LIBRARY_DIR/jsonrpc/jsonrpc_server',
        debug : bool = False
    ):
        self.debug = debug
        procArgs = [ exe_path, '-l', pl_path ]

        if type(consultFile) is list[str]:
            for f in consultFile:
                procArgs += ['-l',f]
        elif type(consultFile) is str:
            procArgs += ['-l', consultFile ]
        elif consultFile is None:
            pass
        else:
            pass

        procArgs += [ '--noinfo', '--nologo' ] if not debug else []
        procArgs += [ '--goal', 'jsonrpc_server_main([call_hook(call)]),halt.' ]

        self.proc = subprocess.Popen(
            procArgs,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            encoding='UTF-8'
        )

    def __del__(self):
        request_quit = json.dumps({'jsonrpc':'2.0','id':self.idcounter ,'method':'quit'})
        self._write_to_proc(request_quit)
        
        m = self._read_from_proc()
        if self.debug:
            print(m)

    #Auto-updating ID counter, so that every write will have an unique ID. To add better logging later.
    @property
    def idcounter(self) -> int:
        self._idcounter += 1
        return self._idcounter - 1

    @idcounter.setter
    def idcounter(self,value : int):
        self._idcounter = value

    def _write_to_proc(self,msg : str) -> None:
        if self.proc.stdin is not None:
            self.proc.stdin.write(msg)
            self.proc.stdin.flush()
        else:
            pass
            # Probably raise some Error? We should never have this issue

    def _read_from_proc(self) -> dict[Any,Any]:
        if self.proc.stdout is not None:
            v = self.proc.stdout.readline()
            return json.loads(v)
        else:
            # Maybe raise some error instead?
            return dict()

    def once(self,goal : str) -> Any:
        msg = json.dumps({'jsonrpc':'2.0','id':self.idcounter ,'method':'once','params':{'goal':goal}})
        self._write_to_proc(msg)
        d = self._read_from_proc()
        if self.debug:
            print(d)
        return d['result']
    
    def state(self, goal : Optional[Any] = None) -> Any:
        if goal is None:
            msg = json.dumps({'jsonrpc':'2.0','id':self.idcounter ,'method':'state'})
        else:
            msg = json.dumps({'jsonrpc':'2.0','id':self.idcounter ,'method':'state','params':[goal]})
        self._write_to_proc(msg)
        d = self._read_from_proc()
        if self.debug:
            print(d)
        return d['result']
    
    def call(self,goal : str) -> Any:
        finished = False
        try:
            msg = json.dumps({'jsonrpc':'2.0','id':self.idcounter ,'method':'call','params':{'goal':goal}})
            self._write_to_proc(msg)

            d = self._read_from_proc()
            while True:
                if self.debug:
                    print(d)
                if 'error' in d:
                    if d['error']['code'] == -4711:
                        #self._cut()
                        finished = True
                        return
                    raise RuntimeError # TODO: Specialize me
                yield d.get("result",None)
                d = self._retry()
        finally:
            if finished is False:
                self._cut()

    def _cut(self) -> None:
        msg = json.dumps({'jsonrpc':'2.0','id':self.idcounter ,'method':'cut'})
        self._write_to_proc(msg)
        d = self._read_from_proc()
        if self.debug:
            print(d)
    
    def _retry(self) -> dict[Any,Any]:
        msg = msg = json.dumps({'jsonrpc':'2.0','id':self.idcounter ,'method':'retry'})
        self._write_to_proc(msg)
        d = self._read_from_proc()
        return d


