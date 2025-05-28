#include <Python.h>
#include <string.h>
#include <stdlib.h>

// Fast XOR operation for large data
static PyObject* fast_xor(PyObject* self, PyObject* args) {
    const char* data;
    const char* key;
    Py_ssize_t data_len, key_len;
    
    if (!PyArg_ParseTuple(args, "y#y#", &data, &data_len, &key, &key_len)) {
        return NULL;
    }
    
    char* result = (char*)malloc(data_len);
    if (!result) {
        return PyErr_NoMemory();
    }
    
    for (Py_ssize_t i = 0; i < data_len; i++) {
        result[i] = data[i] ^ key[i % key_len];
    }
    
    PyObject* py_result = PyBytes_FromStringAndSize(result, data_len);
    free(result);
    return py_result;
}

// Fast entropy calculation
static PyObject* fast_entropy(PyObject* self, PyObject* args) {
    const char* data;
    Py_ssize_t data_len;
    
    if (!PyArg_ParseTuple(args, "y#", &data, &data_len)) {
        return NULL;
    }
    
    int freq[256] = {0};
    for (Py_ssize_t i = 0; i < data_len; i++) {
        freq[(unsigned char)data[i]]++;
    }
    
    double entropy = 0.0;
    for (int i = 0; i < 256; i++) {
        if (freq[i] > 0) {
            double p = (double)freq[i] / data_len;
            entropy -= p * log2(p);
        }
    }
    
    return PyFloat_FromDouble(entropy);
}

// Fast memory clearing
static PyObject* secure_clear(PyObject* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }
    
    if (PyByteArray_Check(obj)) {
        char* data = PyByteArray_AsString(obj);
        Py_ssize_t size = PyByteArray_Size(obj);
        
        // Multiple overwrites for security
        for (int pass = 0; pass < 3; pass++) {
            for (Py_ssize_t i = 0; i < size; i++) {
                data[i] = (char)(rand() & 0xFF);
            }
        }
        memset(data, 0, size);
    }
    
    Py_RETURN_NONE;
}

// Method definitions
static PyMethodDef fastCrypteroMethods[] = {
    {"fast_xor", fast_xor, METH_VARARGS, "Fast XOR operation"},
    {"fast_entropy", fast_entropy, METH_VARARGS, "Fast entropy calculation"},
    {"secure_clear", secure_clear, METH_VARARGS, "Secure memory clearing"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef fastCrypteromodule = {
    PyModuleDef_HEAD_INIT,
    "fast_crypto",
    "Fast cryptographic operations in C",
    -1,
    fastCrypteroMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_fast_crypto(void) {
    return PyModule_Create(&fastCrypteromodule);
} 