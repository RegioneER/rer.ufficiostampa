import React, { useState, useEffect, useContext } from 'react';
import { TranslationsContext } from '../TranslationsContext';
import { SubscriptionsContext } from '../SubscriptionsContext';
import apiFetch from '../utils/apiFetch';
import Modal from '../Modal/Modal';
import TextField from '../common/Field';
import { getUserFieldsLables } from '../utils/utils';
import './EditUser.less';

const isValidEmail = email => {
  const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
};

const EditUser = ({ user }) => {
  const getTranslationFor = useContext(TranslationsContext);
  const { subscriptions, portalUrl, fetchSubscriptions } = useContext(
    SubscriptionsContext,
  );

  const [showModal, setShowModal] = useState(user != null);
  const [serverError, setServerError] = useState(null);

  const labels = getUserFieldsLables(getTranslationFor);

  useEffect(() => {
    if (user != null) {
      setEditUser(JSON.parse(JSON.stringify(user)));
      setValidationErrors({});
      setShowModal(true);
    }
  }, [user]);

  const [editUser, setEditUser] = useState({});
  const [validationErrors, setValidationErrors] = useState({});

  const changeUserField = (id, value) => {
    let u = { ...editUser, [id]: value };
    setEditUser(u);
    validateUser(u);
  };

  const validateUser = u => {
    const validation = {};

    if (!u.email) {
      validation.email = `${labels.email} ${getTranslationFor(
        'is required',
        'is required',
      )}`;
    } else if (!isValidEmail(u.email)) {
      validation.email = `${labels.email} ${getTranslationFor(
        'is not valid',
        'is not valid',
      )}`;
    }

    if (!u.channels || u.channels.length == 0) {
      validation.channels = `${getTranslationFor(
        'Select at least one channel',
        'Select at least one channel',
      )}`;
    }
    setValidationErrors(validation);
  };

  const submit = () => {
    let url = portalUrl + '/@subscriptions';
    let method = 'POST';

    if (editUser.id) {
      url += '/' + editUser.id;
      method = 'PATCH';
    }

    const fetches = [
      apiFetch({
        url: url,
        params: editUser,
        method: method,
      }),
    ];

    Promise.all(fetches).then(data => {
      const res = data[0];

      if (res.status == 204) {
        //OK
        setShowModal(false);
        fetchSubscriptions();
      } else {
        setServerError(res);
      }
    });
  };

  return (
    <Modal show={showModal} close={() => setShowModal(false)}>
      <Modal.Body>
        <div className="edit-user">
          <h1>
            {editUser['@id']
              ? getTranslationFor('Edit Subscriber', 'Edit Subscriber')
              : getTranslationFor('Add Subscriber', 'Add Subscriber')}
          </h1>

          {serverError && (
            <dl class="portalMessage error" role="alert">
              <dt>Error. Status code: {serverError.status}</dt>
              <dd>{res.statusText}</dd>
            </dl>
          )}

          <form>
            <TextField
              name="name"
              label={labels.name}
              value={editUser.name}
              onChange={changeUserField}
              errors={validationErrors}
            />
            <TextField
              name="surname"
              label={labels.surname}
              value={editUser.surname}
              onChange={changeUserField}
              errors={validationErrors}
            />
            <TextField
              name="email"
              label={labels.email}
              value={editUser.email}
              onChange={changeUserField}
              required={true}
              errors={validationErrors}
            />
            <TextField
              name="phone"
              label={labels.phone}
              value={editUser.phone}
              onChange={changeUserField}
              errors={validationErrors}
            />
            <TextField
              name="newspaper"
              label={labels.newspaper}
              value={editUser.newspaper}
              onChange={changeUserField}
              errors={validationErrors}
            />
            <TextField
              name="channels"
              label={labels.channels}
              value={editUser.channels ?? []}
              onChange={changeUserField}
              required={true}
              errors={validationErrors}
              type="multiselect"
              options={subscriptions.channels}
              confirmRemove={true}
            />
          </form>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <button
          onClick={() => {
            submit();
          }}
          className="plone-btn plone-btn-primary"
          disabled={
            Object.keys(editUser).length == 0 ||
            Object.keys(validationErrors).length > 0
          }
        >
          {getTranslationFor('save', 'Save')}
        </button>
      </Modal.Footer>
    </Modal>
  );
};
export default EditUser;
