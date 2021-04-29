import React, { useContext, useState } from 'react';
import Select from 'react-select';
import { string, shape, arrayOf, func, bool, object } from 'prop-types';
import { TranslationsContext } from '../../../TranslationsContext';
import { DateRangePicker } from 'react-dates';

import 'react-dates/initialize';
import 'react-dates/lib/css/_datepicker.css';
import './DateField.less';

const DateField = ({
  parameter,
  value = {},
  updateQueryParameters,
  isMobile,
}) => {
  const getTranslationFor = useContext(TranslationsContext);
  const [focusedDateInput, setFocusedDateInput] = useState(null);
  return (
    <React.Fragment>
      <label htmlFor={parameter.id}>{parameter.label}</label>
      {parameter.help.length ? (
        <p className="discreet">{parameter.help}</p>
      ) : (
        ''
      )}
      <DateRangePicker
        startDateId="start-date-filter"
        startDate={value?.from}
        startDatePlaceholderText={getTranslationFor('from_label', 'From')}
        endDate={value?.to}
        endDateId="end-date-filter"
        endDatePlaceholderText={getTranslationFor('to_label', 'To')}
        onDatesChange={({ startDate, endDate }) => {
          updateQueryParameters({
            [parameter.id]: { from: startDate, to: endDate },
          });
        }}
        noBorder={true}
        numberOfMonths={isMobile ? 1 : 2}
        focusedInput={focusedDateInput}
        onFocusChange={focusedInput => setFocusedDateInput(focusedInput)}
        displayFormat="DD/MM/YYYY"
        hideKeyboardShortcutsPanel={true}
        showClearDates={true}
        minimumNights={0}
        isOutsideRange={() => {}}
      />
    </React.Fragment>
  );
};

DateField.propTypes = {
  parameter: shape({
    id: string,
    options: arrayOf(shape({ label: string, value: string })),
    multivalued: bool,
  }),
  value: object,
  updateQueryParameters: func,
};

export default DateField;
