from abc import abstractmethod,ABC
from plcom import SicstusCommunicator
from typing import TypeVar,Generic,Any,Union,Type,Literal,Optional


T = TypeVar('T')
sp_valid_primitives_t = Union[int,str,list['sp_valid_arg_t']]
sp_valid_arg_t = Union[sp_valid_primitives_t,'SPTerm']


class SicstusSymbolic(SicstusCommunicator):
    _channel : int
    def __init__(self,
        consultFile : Union[None,str,list[str]] = None,
        exe_path : str = 'sicstus',
        pl_path : str = '$SP_LIBRARY_DIR/jsonrpc/jsonrpc_server',
        debug : bool = False
    ) -> None:
        super().__init__(consultFile=consultFile,exe_path=exe_path,pl_path=pl_path,debug=debug)

    def newFunctor(self,name : str, arity : int, bound : bool = False) -> 'SPFunctor':
        return SPFunctor(parent=self,name=name,arity=arity,bound=bound)

    def newVariable(self,name : str) -> 'SPVariable[Any]':
        return SPVariable[Any](parent=self,name=name)


    def query(self, a : list['SPTerm']):
        freevars = set[SPVariable[Any]]()
        lx = list[str]()
        for item in a:
            vars, s = _convertElement(item)
            freevars = freevars | vars
            lx.append(s)


        varslist = list(filter(lambda x: x.name != '_', freevars))
        toCall : str = ','.join(lx) + ",Result=[" + ','.join(map(lambda x: x.name,varslist)) + "]" + '.'

        for Result in self.call(toCall):
            for i in range(len(varslist)):
                varslist[i]._value = Result[i] # type: ignore
            yield True
        return False

        




class SPTerm(ABC):
    _arity : int
    _name : str
    _parent : SicstusSymbolic
    def __init__(self,parent : SicstusSymbolic, name : str, arity : int):
        self._parent = parent
        self._name = name
        self._arity = arity

    @property
    def name(self) -> str:
        return self._name

    @property
    def arity(self) -> int:
        return self._arity

    @abstractmethod
    def convert(self) -> tuple[set['SPVariable[Any]'],str]:
        pass

class SPVariable(SPTerm,Generic[T]):
    _value : Union[T,None] = None
    def __init__(self, parent : SicstusSymbolic, name : str):
        if not name[0].isupper() and not name[0] == '_':
            raise RuntimeError
        super().__init__(parent,name,0)

    @property
    def value(self) -> T:
        if self._value is not None:
            return self._value
        raise RuntimeError
    
    def load(self,value : T):
        try: self._value
        except AttributeError:
            self._value = value
    
    def is_(self, arg : Any, sign : Union[Literal["eq"],Literal["is"]] = "is"):
        return SPAssignment(self._parent,self,arg,sign)

    @property
    def eq(self):
        pass

    @eq.setter
    def eq(self,val:Any):
        return SPAssignment(self._parent,self,val,sign="eq")

    def convert(self) -> tuple[set['SPVariable[Any]'],str]:
        return (set([self]),self._name)

class SPAssignment(SPTerm):
    _args : sp_valid_arg_t
    _source : SPVariable[Any]
    _sign : Literal["="," is "]
    def __init__(self, parent : SicstusSymbolic, source : SPVariable[Any], arg : sp_valid_arg_t,sign : Literal["eq","is"] = "eq"):
        if sign=="eq":
            self._sign = "="
        elif sign=="is":
            self._sign = " is "
        else:
            raise TypeError
        
        name = str(source) + self._sign + str(arg) 
        super().__init__(parent,name,0)
        self._args = arg
        self._source = source
    
    def convert(self) -> tuple[set['SPVariable[Any]'],str]:
        argvar, argstring = _convertElement(self._args)

        return (argvar | set([self._source]), self._source._name + self._sign + argstring) 



class SPList(SPTerm):
    def __init__(self,):
        pass

class SPStructure(SPTerm):
    _args : tuple[sp_valid_arg_t,...]
    def __init__(self, parent : SicstusSymbolic, name : str, arity : int, args : tuple[sp_valid_arg_t,...]):
        super().__init__(parent,name,arity)
        self._args = args
    
    def convert(self) -> tuple[set['SPVariable[Any]'],str]:
        allvar = set[SPVariable[Any]]()
        lx = list[str]()
        for item in self._args:
            var,string = _convertElement(item)
            allvar = allvar | var
            lx.append(string)

        retstr = self._name + '(' +  ','.join(lx) + ')'
        return (allvar, retstr)


class SPFunctor(SPTerm):
    _name : str
    _arity : int
    _parent : SicstusSymbolic
    def __init__(self, name : str, arity : int, parent : SicstusSymbolic, bound : bool=False):
        if not name[0].islower() and name[0] != '_':
            raise RuntimeError
        self._name = name
        self._arity = arity
        self._bound = bound
        self._parent = parent


    def __call__(self,*args : sp_valid_arg_t):
        if len(args) != self._arity:
            raise RuntimeWarning
        return SPStructure(self._parent,self._name,self._arity,args)
    
    def convert(self) -> tuple[set['SPVariable[Any]'],str]:
        raise RuntimeError

    def addRule(self,head : tuple[Any,...],body : Optional[list[Any]] = None):
        lx = list[str]()
        for item in head:
            _,s = _convertElement(item)
            lx.append(s)

        command = 'assert((' + self._name + '(' + ','.join(lx) + ')'
        if body is not None:
            raise NotImplementedError
        command += ')).'
        self._parent.once(command)


def _convertElement(o : Union[SPTerm,sp_valid_primitives_t]) -> tuple[set[SPVariable[Any]],str]:
    if type(o) is int:
        return (set(),str(o))
    elif type(o) is str:
        return (set(),o)
    elif type(o) is list:#[Union[SPTerm,sp_valid_primitives_t]]:
        s = set[SPVariable[Any]]()
        lx = list[str]()
        
        item : Union[SPTerm,sp_valid_primitives_t]
        for item in o: # type: ignore
            s_, string = _convertElement(item)
            s = s | s_
            lx.append(string)
        return s,'[' + ','.join(lx) + ']'
    elif issubclass(type(o), SPTerm):
        var,string = o.convert() # type: ignore
        return (var,string) # type: ignore
    else:
        print(o)
        raise TypeError


'''
try: 
    _sicstus_sessions : dict[int,_SicstusSymbolic]
except NameError:
    _sicstus_sessions = {}


def init_SicstusSymbolicSession(channel : int = 0):
    _sicstus_sessions[channel] = _SicstusSymbolic(channel)



class Variable(Term,Generic[T]):
    _name : str
    _value : T
    _channel : int
    def __init__(self, name : str, channel : int = 0):
        if not name[0].isupper():
            raise RuntimeError
        self._name = name
        self._channel = channel

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def value(self) -> T:
        return self._value
    
    def bind(self,value : T):
        pass




class Functor(Term):
    _name : str
    _arity : int
    _channel : int
    def __init__(self, name : str, arity : int, bound : bool=False,channel : int = 0):
        if not name[0].islower():
            raise RuntimeError
        self._name = name
        self._arity = arity
        self._bound = bound
        self._channel = channel

    @property
    def name(self) -> str:
        return self._name

    @property
    def arity(self) -> int:
        return self._arity

    def __call__(self,*args : Any):
        if len(args) != self._arity:
            raise RuntimeWarning
        return Term(self._arity,args)

    def addRule(self,head : tuple[Any,...],body : list[Any]):
        pass




Statement = Union[list[Term],tuple[Term,...]]

'''