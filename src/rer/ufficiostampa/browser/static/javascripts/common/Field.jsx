import React, { useState, useEffect, useContext } from 'react';
import { TranslationsContext } from '../TranslationsContext';
import Modal from '../Modal/Modal';

import './Field.less';

const isValidEmail = email => {
  const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(String(email).toLowerCase());
};

const Field = ({
  name,
  label,
  value,
  onChange,
  required,
  errors,
  type = 'text',
  options = [], //for type 'multiselect'
}) => {
  const getTranslationFor = useContext(TranslationsContext);

  return (
    <div className={`field ${type}`}>
      <label htmlFor={`formfield-${name}`} className="horizontal">
        {label}
        {required && (
          <span
            className="required horizontal"
            title={getTranslationFor('Required', 'Obbligatorio')}
          >
            &nbsp;
          </span>
        )}
      </label>

      {errors[name] && <div className="fieldErrorBox">{errors[name]}</div>}

      {/* ------- text -------- */}
      {type == 'text' && (
        <input
          id={`formfield-${name}`}
          name={name}
          value={value ?? ''}
          onChange={event => {
            onChange(name, event.target.value);
          }}
          type="text"
        />
      )}

      {/* ------- multiselect -------- */}
      {type == 'multiselect' && (
        <div className="multiselection">
          {options.map((opt, index) => (
            <span className="option" key={name + '-opt-' + index}>
              <input
                type="checkbox"
                id={`formfield-${name}-opt-${index}`}
                name={`formfield-${name}-list`}
                className="checkbox-widget tuple-field"
                value={opt}
                checked={value?.indexOf(opt) >= 0 ? 'checked' : false}
                onChange={() => {
                  let v = JSON.parse(JSON.stringify(value ?? []));
                  if (v.indexOf(opt) >= 0) {
                    v.splice(v.indexOf(opt), 1);
                  } else {
                    v.push(opt);
                  }
                  onChange(name, v);
                }}
              />
              <label htmlFor={`formfield-${name}-opt-${index}`}>
                <span className="label">{opt}</span>
              </label>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
export default Field;
