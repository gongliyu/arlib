ChangeLog
=========

.. currentmodule:: arlib

0.0.4
-----
* Add :func:`arlib.open` as a shortcut of :class:`Archive` constructor
  (:issue:`1`, :pr:`2`).
* Add :func:`is_archive` to determine if a file could be opened
  as a valid archive (:issue:`3`, :pr:`4`).
* Add :func:`assert_is_archive` (:pr:`5`).
* Reimplement auto_engine mechanism using *decoutils* package
* Add functionality to check whether a member is a directory or
  regular file (:pr:`9`).
* Add functionality to extract members (:pr:`10`).

0.0.3
-----

* Support tar, zip files and folder
* Automatic archive type deduction
* Support member names listing
* Support opening members as file streams
  
