import React, { useEffect } from 'react';
import { object, func, bool } from 'prop-types';
import TextField from '../fields/TextField';
import SelectField from '../fields/SelectField';
import CheckboxField from '../fields/CheckboxField';
import DateField from '../fields/DateField';

import './index.less';

const FieldWrapper = ({
  parameter,
  queryParameters,
  updateQueryParameters,
  isMobile,
}) => {
  let FieldComponent = '';
  let className = '';
  const { hidden, id, type } = parameter;
  const value = queryParameters[id];
  if (hidden) {
    return '';
  }
  switch (type) {
    case 'select':
      FieldComponent = SelectField;
      className = 'select';
      break;
    case 'checkbox':
      FieldComponent = CheckboxField;
      className = 'checkbox';
      break;
    case 'date':
      FieldComponent = DateField;
      className = 'date';
      break;
    default:
      FieldComponent = TextField;
      className = 'text';
  }
  return (
    <div className={`field ${className}-field`}>
      <FieldComponent
        parameter={parameter}
        value={value}
        updateQueryParameters={updateQueryParameters}
        isMobile={isMobile}
      />
    </div>
  );
};

const FormFieldWrapper = ({
  parameter,
  queryParameters,
  updateQueryParameters,
  isMobile,
}) => {
  const { slave, id } = parameter;

  let params = [
    <FieldWrapper
      parameter={parameter}
      queryParameters={queryParameters}
      updateQueryParameters={updateQueryParameters}
      isMobile={isMobile}
      key={0}
    />,
  ];
  if (slave) {
    const masterValue = queryParameters[id];
    let filteredValues = [];
    for (const [key, values] of Object.entries(slave.slaveOptions)) {
      if (
        !masterValue ||
        masterValue.length === 0 ||
        masterValue.includes(key)
      ) {
        filteredValues.push(...values);
      }
    }
    // remove duplicates
    const slaveValues = filteredValues.filter((value, index) => {
      const _value = JSON.stringify(value);
      return (
        index ===
        filteredValues.findIndex(obj => {
          return JSON.stringify(obj) === _value;
        })
      );
    });
    slaveValues.sort((a, b) => {
      const nameA = a.value.toUpperCase(); // ignore upper and lowercase
      const nameB = b.value.toUpperCase(); // ignore upper and lowercase
      if (nameA < nameB) {
        return -1;
      }
      if (nameA > nameB) {
        return 1;
      }

      // names must be equal
      return 0;
    });
    params.push(
      <FieldWrapper
        parameter={{ ...slave, options: slaveValues }}
        queryParameters={queryParameters}
        updateQueryParameters={updateQueryParameters}
        isMobile={isMobile}
        key={1}
      />,
    );
  }

  return <React.Fragment>{params}</React.Fragment>;
};

FieldWrapper.propTypes = {
  parameter: object,
  updateQueryParameters: func,
  queryParameters: object,
  isMobile: bool,
};

FormFieldWrapper.propTypes = {
  parameter: object,
  updateQueryParameters: func,
  queryParameters: object,
  isMobile: bool,
};

export default FormFieldWrapper;
