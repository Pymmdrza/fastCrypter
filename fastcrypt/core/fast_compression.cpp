#include <Python.h>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <cstring>

extern "C" {

// Fast LZ77-style compression
static PyObject* fast_compress(PyObject* self, PyObject* args) {
    const char* data;
    Py_ssize_t data_len;
    
    if (!PyArg_ParseTuple(args, "y#", &data, &data_len)) {
        return NULL;
    }
    
    std::vector<char> compressed;
    compressed.reserve(data_len);
    
    std::unordered_map<std::string, size_t> dictionary;
    
    for (size_t i = 0; i < static_cast<size_t>(data_len); ) {
        size_t match_len = 0;
        size_t match_pos = 0;
        
        // Look for matches in sliding window
        for (size_t len = 3; len <= 258 && i + len <= static_cast<size_t>(data_len); len++) {
            std::string substr(data + i, len);
            auto it = dictionary.find(substr);
            if (it != dictionary.end() && it->second < i) {
                match_len = len;
                match_pos = it->second;
            }
        }
        
        if (match_len >= 3) {
            // Encode match
            compressed.push_back(0xFF); // Match marker
            compressed.push_back(static_cast<char>(match_len));
            compressed.push_back(static_cast<char>(i - match_pos));
            i += match_len;
        } else {
            // Literal byte
            compressed.push_back(data[i]);
            i++;
        }
        
        // Update dictionary
        if (i >= 3) {
            std::string key(data + i - 3, 3);
            dictionary[key] = i - 3;
        }
    }
    
    return PyBytes_FromStringAndSize(compressed.data(), compressed.size());
}

// Fast decompression
static PyObject* fast_decompress(PyObject* self, PyObject* args) {
    const char* data;
    Py_ssize_t data_len;
    
    if (!PyArg_ParseTuple(args, "y#", &data, &data_len)) {
        return NULL;
    }
    
    std::vector<char> decompressed;
    decompressed.reserve(data_len * 2);
    
    for (size_t i = 0; i < static_cast<size_t>(data_len); ) {
        if (data[i] == static_cast<char>(0xFF) && i + 2 < static_cast<size_t>(data_len)) {
            // Match found
            size_t length = static_cast<unsigned char>(data[i + 1]);
            size_t distance = static_cast<unsigned char>(data[i + 2]);
            
            size_t start_pos = decompressed.size() - distance;
            for (size_t j = 0; j < length; j++) {
                decompressed.push_back(decompressed[start_pos + j]);
            }
            i += 3;
        } else {
            // Literal byte
            decompressed.push_back(data[i]);
            i++;
        }
    }
    
    return PyBytes_FromStringAndSize(decompressed.data(), decompressed.size());
}

// Fast byte frequency analysis
static PyObject* fast_analyze(PyObject* self, PyObject* args) {
    const char* data;
    Py_ssize_t data_len;
    
    if (!PyArg_ParseTuple(args, "y#", &data, &data_len)) {
        return NULL;
    }
    
    std::vector<int> freq(256, 0);
    for (size_t i = 0; i < static_cast<size_t>(data_len); i++) {
        freq[static_cast<unsigned char>(data[i])]++;
    }
    
    PyObject* result = PyList_New(256);
    for (int i = 0; i < 256; i++) {
        PyList_SetItem(result, i, PyLong_FromLong(freq[i]));
    }
    
    return result;
}

// Method definitions
static PyMethodDef FastCompressionMethods[] = {
    {"fast_compress", fast_compress, METH_VARARGS, "Fast compression"},
    {"fast_decompress", fast_decompress, METH_VARARGS, "Fast decompression"},
    {"fast_analyze", fast_analyze, METH_VARARGS, "Fast byte analysis"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef fastcompressionmodule = {
    PyModuleDef_HEAD_INIT,
    "fast_compression",
    "Fast compression operations in C++",
    -1,
    FastCompressionMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_fast_compression(void) {
    return PyModule_Create(&fastcompressionmodule);
}

} // extern "C" 