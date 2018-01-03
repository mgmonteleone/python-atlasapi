Docs with sphinx
----------------

Local documentation
^^^^^^^^^^^^^^^^^^^

.. code:: bash
    
    cd gendocs
    make clean
    make html
    python -m RangeHTTPServer
    
Update docs
^^^^^^^^^^^

.. code:: bash
    
    cd gendocs
    make clean
    make html
    rsync -crv --delete --exclude=README.rst _build/html/ ../docs/
    
