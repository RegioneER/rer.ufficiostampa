.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

===================
RER: Ufficio Stampa
===================

Prodotto per la gestione delle comunicazioni alla stampa.

Funzionalità principali
=======================

- Content-type dedicati (Comunicato Stampa e Invito Stampa)
- Gestione canali di iscrizioni per i giornalisti
- Invio dei comunicati

Content-type
============

Sono presenti due content-type uguali tra loro per la gestione di due tipi diversi di comunicazioni:

- **Comunicato Stampa**
- **Invito Stampa**

Sono delle pagine con due campi aggiuntivi (Argomenti e Legislatura) e folderish (in cui si può inserire solo **Immagini**, **File** e **Cartelle**).

Database iscritti
=================

C'è un database interno (basato su `souper.plone <https://pypi.org/project/souper.plone/>`_) nel quale vengono memorizzati i dati degli iscritti.

E' possibile interrogare il database tramite rotte api (vedi in seguito) o mediante utility Plone::

    from zope.component import getUtility
    from rer.ufficiostampa.interfaces import ISubscriptionsStore

    tool = getUtility(ISubscriptionsStore)

Di seguito vengono riportati i principali metodi.

Aggiunta iscritto
-----------------

- Metodo ``add``
- Parametri: ``data`` (dizionario con i parametri)
- Risposta: l'id univoco del nuovo record

``data`` deve essere un dizionario con la lista di possibili parametri:

- email [obbligatorio]: indirizzo a cui inviare i comunicati
- channels [obbligatorio]: lista dei canali di invio di interesse
- name: nome dell'iscritto
- surname: cognome dell'iscritto
- phone: numero di telefono dell'iscritto
- newspaper: nome della testata giornalistica di riferimento dell'iscritto

Altri campi verranno ignorati.

Ricerca iscritti
----------------

- Metodo ``search``
- Parametri: ``query`` (dizionario con i parametri), ``sort_index`` (default=date), ``reverse`` (default=False)
- Risposta: la lista di risultati

``query`` è un dizionario che può contenere uno o più dei seguenti parametri:

- text (viene ricercato nei campi nome, email e cognome)
- channels
- newspaper

Aggiornamento dati iscritto
---------------------------

- Metodo ``update``
- Parametri: ``data`` (dizionario con i parametri), ``id`` (identificativo dell'iscritto)
- Risposta: 

``data`` è un dizionario che può contenere uno o più dei parametri di iscrizione.

Cancellazione iscritto
-----------------------

- Metodo ``delete``
- Parametri: ``id`` (identificativo dell'iscritto)
- Risposta: 

Reset database
--------------

- Metodo ``clear``
- Parametri:
- Risposta: 


Rotte restapi
=============

Lista iscritti
--------------

*@subscriptions*

Endpoint da chiamare in **GET** sulla radice del sito.

Ritorna la lista degli iscritti e i possibili canali. Solo per gli utenti che hanno il permesso "rer.ufficiostampa.ManageChannels"::

> curl -i -X GET http://localhost:8080/Plone/@subscriptions -H 'Accept: application/json' -H 'Content-Type: application/json' --user admin:admin

La risposta è simile a questa::

    {
        "@id": "http://localhost:8080/Plone/@subscriptions",
        "items": [
            ...
        ],
        "items_total": 42,
        "channels": [...]
    }


Creazione nuovo iscritto
------------------------

*@subscriptions*

Endpoint da chiamare in **POST** sulla radice del sito.

Solo per gli utenti che hanno il permesso "rer.ufficiostampa.ManageChannels"::

> curl -i -X POST http://localhost:8080/Plone/@subscriptions -H 'Accept: application/json' -H 'Content-Type: application/json' --data-raw '{"email": "foo@plone.org", "channels": ["first", "second"]}' --user admin:admin

Se l'operazione va a buon fine, il server ritorna un ``204``.



Aggiornamento dati iscritto
---------------------------

*@subscriptions*

Endpoint da chiamare in **PATCH** sulla radice del sito.

Solo per gli utenti che hanno il permesso "rer.ufficiostampa.ManageChannels"::

> curl -i -X PATCH http://localhost:8080/Plone/@subscriptions/subscription_id -H 'Accept: application/json' -H 'Content-Type: application/json' --data-raw '{"email": "foo@plone.org", "name": "John"}' --user admin:admin

Dove **subscription_id** è l'id dell'iscritto da aggiornare.

Se l'operazione va a buon fine, il server ritorna un ``204``.

Valgono le regole dei campi per la creazione.

Cancellazione iscritto
----------------------

*@subscriptions*

Endpoint da chiamare in **DELETE** sulla radice del sito.

Solo per gli utenti che hanno il permesso "rer.ufficiostampa.ManageChannels"::

> curl -i -X DELETE http://localhost:8080/Plone/@subscriptions/subscription_id -H 'Accept: application/json' --user admin:admin

Dove **subscription_id** è l'id dell'iscritto da aggiornare.

Se l'operazione va a buon fine, il server ritorna un ``204``.


Cancellazione iscritto
----------------------

*@subscriptions-clear*

Endpoint da chiamare in **GET** sulla radice del sito.

Solo per gli utenti che hanno il permesso "rer.ufficiostampa.ManageChannels"::

> curl -i -X DELETE http://localhost:8080/Plone/@subscriptions-clear -H 'Accept: application/json' --user admin:admin

Svuota completamente il db degli iscritti.

Se l'operazione va a buon fine, il server ritorna un ``204``.


Sviluppo
========


Installazione
=============

Install rer.ufficiostampa by adding it to your buildout::

    [buildout]

    ...

    eggs =
        rer.ufficiostampa


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/rer.ufficiostampa/issues
- Source Code: https://github.com/collective/rer.ufficiostampa
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@example.com


License
-------

The project is licensed under the GPLv2.
