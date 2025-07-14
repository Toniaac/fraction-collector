from ctypes import *

class ElveflowMUXWrapper:
    def __init__(self, dll_path=r'DLL64\Elveflow64.dll'):
        self.dll = CDLL(dll_path)
        self._bind_mux_functions()

    def _bind_mux_functions(self):
        self._MUX_Initialization = self._bind('MUX_Initialization', [c_char_p, POINTER(c_int32)])
        self._MUX_Set_all_valves = self._bind('MUX_Set_all_valves', [c_int32, POINTER(c_int32), c_int32])
        self._MUX_Wire_Set_all_valves = self._bind('MUX_Wire_Set_all_valves', [c_int32, POINTER(c_int32), c_int32])
        self._MUX_Destructor = self._bind('MUX_Destructor', [c_int32])
        self._MUX_Get_Trig = self._bind('MUX_Get_Trig', [c_int32, POINTER(c_int32)])
        self._MUX_Set_Trig = self._bind('MUX_Set_Trig', [c_int32, c_int32])
        self._MUX_Set_indiv_valve = self._bind('MUX_Set_indiv_valve', [c_int32, c_int32, c_int32, c_int32])
        self._MUX_Get_valves_Type = self._bind('MUX_Get_valves_Type', [c_int32, POINTER(c_int32), c_int32])
        self._MUX_Set_valves_Type = self._bind('MUX_Set_valves_Type', [c_int32, c_int32])

    def _bind(self, func_name, argtypes):
        fn = getattr(self.dll, func_name)
        fn.argtypes = argtypes
        return fn

    def initialize(self, device_name: str) -> int:
        mux_id = c_int32()
        err = self._MUX_Initialization(device_name.encode('ascii'), byref(mux_id))
        return mux_id.value if err == 0 else -1

    def set_all_valves(self, mux_id: int, state: int) -> int:
        array_type = c_int32 * 16
        valve_array = array_type(*([state] * 16))
        return self._MUX_Set_all_valves(mux_id, valve_array, 16)

    def wire_set_all_valves(self, mux_id: int, pattern=None) -> int:
        if pattern is None:
            pattern = [(i % 2) for i in range(16)]
        valve_array = (c_int32 * 16)(*pattern)
        return self._MUX_Wire_Set_all_valves(mux_id, valve_array, 16)

    def set_individual_valve(self, mux_id: int, input_valve: int, output_valve: int, state: int) -> int:
        return self._MUX_Set_indiv_valve(mux_id, input_valve, output_valve, state)

    def get_trigger(self, mux_id: int) -> str:
        trig = c_int32()
        err = self._MUX_Get_Trig(mux_id, byref(trig))
        if err != 0:
            raise RuntimeError("Failed to get trigger status.")
        return 'high' if trig.value else 'low'

    def set_trigger(self, mux_id: int, high: bool) -> int:
        return self._MUX_Set_Trig(mux_id, 1 if high else 0)

    def set_valve_type(self, mux_id: int, valve_number: int, valve_type: int) -> int:
        return self._MUX_Set_valves_Type(mux_id, valve_number, valve_type)

    def get_valve_types(self, mux_id: int) -> list:
        types_array = (c_int32 * 8)()
        err = self._MUX_Get_valves_Type(mux_id, types_array, 8)
        if err != 0:
            raise RuntimeError("Failed to get valve types.")
        return list(types_array)

    def destructor(self, mux_id: int) -> int:
        return self._MUX_Destructor(mux_id)

    def debug_status(self):
        Status = self.dll.LVDLLStatus
        Status.argtypes = [c_char_p, c_int32, c_void_p]
        err_str = create_string_buffer(256)
        err_len = c_int(len(err_str))
        module = None
        result = Status(err_str, err_len, module)
        print(f"Function returned: {result}")
        print(f"Error message: {err_str.value.decode()}")
