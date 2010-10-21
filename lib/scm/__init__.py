# coding: utf-8


def get_scm_class(scm_name):
    scm_module_name = scm_name.lower()
    scm_class_name = scm_name.capitalize()
    
    scm_module = __import__("lib.scm.%s" % scm_module_name, '', '',
        [scm_class_name])

    return getattr(scm_module, scm_class_name)
