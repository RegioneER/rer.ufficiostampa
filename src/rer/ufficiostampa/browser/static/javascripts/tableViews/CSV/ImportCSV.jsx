import React, { useState, useEffect, useContext } from 'react';
import DataTable from 'react-data-table-component';
import Select from 'react-select';
import { TranslationsContext } from '../../TranslationsContext';
import { ApiContext } from '../../ApiContext';
import apiFetch from '../../utils/apiFetch';
import Modal from '../Modal/Modal';
import Field from '../common/Field';

import './ImportCSV.less';

const ImportCSV = ({ showModal = false, setShowModal }) => {
  const getTranslationFor = useContext(TranslationsContext);
  const { data, portalUrl, fetchApi } = useContext(ApiContext);

  const [serverError, setServerError] = useState(null);
  const [formData, setFormData] = useState({});
  const [validationErrors, setValidationErrors] = useState({});
  const [importResult, setImportResult] = useState(null);

  useEffect(() => {
    if (showModal) {
      setImportResult(null);
      setServerError(null);
      setFormData({});
      setValidationErrors({});
    }
  }, [showModal]);

  const changeField = (id, value) => {
    let fd = { ...formData, [id]: value };

    setFormData(fd);
    validateFormData(fd);
  };

  const validateFormData = fd => {
    const validation = {};
    if (!fd.file) {
      validation.file = `${getTranslationFor(
        'File',
        'File',
      )} ${getTranslationFor('is required', 'is required')}`;
    }
    setValidationErrors(validation);
  };

  const submit = () => {
    let url = portalUrl + '/@subscriptions-csv';
    let method = 'POST';

    let data = {
      ...formData,
      file: {
        data: formData.file.base64,
        encoding: 'base64',
        'content-type': 'text/comma-separated-values',
        filename: formData.file.name,
      },
    };

    const fetches = [
      apiFetch({
        url: url,
        params: data,
        method: method,
      }),
    ];

    Promise.all(fetches).then(data => {
      const res = data[0];
      console.log('res', res);
      if (res.status == 200) {
        //OK
        //setShowModal(false);
        console.log(res.data);
        setImportResult(res.data);
        fetchApi();
      } else {
        setServerError(res);
      }
    });
  };

  return (
    <Modal
      show={showModal}
      close={() => setShowModal(false)}
      className="modal-import-csv"
      id="modal-import-csv"
    >
      <Modal.Body>
        <div className="import-csv">
          <h1 id="modal-import-csv_label">
            {getTranslationFor('Import from CSV', 'Import from CSV')}
          </h1>

          {serverError && (
            <dl className="portalMessage error" role="alert">
              <dt>Error. Status code: {serverError.status}</dt>
              <dd>{serverError.statusText}</dd>
            </dl>
          )}

          {importResult ? (
            <div className="portalMessage alert-success import-result">
              <div>
                <strong>
                  {getTranslationFor('Imported rows', 'Imported rows')}:{' '}
                </strong>
                {importResult.imported}
              </div>
              <div>
                <strong>
                  {getTranslationFor('Skipped rows', 'Skipped rows')}:{' '}
                </strong>
                {importResult.skipped?.length ? '' : 0}
                {importResult.skipped?.map(s => (
                  <div className="skipped-row">
                    {getTranslationFor('Row', 'Row')} {s}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <form>
              <Field
                name="file"
                label={getTranslationFor('File', 'File')}
                value={formData.file}
                type="file"
                onChange={changeField}
                required={true}
                errors={validationErrors}
              />

              <Field
                name="overwrite"
                label={getTranslationFor(
                  'Overwrite duplicates',
                  'Overwirte duplicates',
                )}
                value={formData.overwrite}
                onChange={changeField}
                errors={validationErrors}
                type="checkbox"
              />
              <Field
                name="clean"
                label={getTranslationFor(
                  'Clean all data before import',
                  'Clean all data before import',
                )}
                value={formData.clean}
                onChange={changeField}
                errors={validationErrors}
                type="checkbox"
              />
            </form>
          )}
        </div>
      </Modal.Body>
      {!importResult && (
        <Modal.Footer>
          <button
            onClick={() => {
              submit();
            }}
            className="plone-btn plone-btn-primary"
            disabled={
              Object.keys(formData).length == 0 ||
              Object.keys(validationErrors).length > 0
            }
          >
            {getTranslationFor('save', 'Save')}
          </button>
        </Modal.Footer>
      )}
    </Modal>
  );
};
export default ImportCSV;
