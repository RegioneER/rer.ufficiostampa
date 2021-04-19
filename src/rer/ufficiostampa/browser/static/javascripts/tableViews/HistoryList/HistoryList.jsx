import React, { useState, useEffect, useContext } from 'react';
import DataTable from 'react-data-table-component';
import format from 'date-fns/format';
import { TranslationsContext } from '../../TranslationsContext';
import Select from 'react-select';
import {
  ApiContext,
  DEFAULT_B_SIZE,
  DEFAULT_SORT_ON,
  DEFAULT_SORT_ORDER,
} from '../../ApiContext';
import apiFetch from '../../utils/apiFetch';
import { getHistoryFieldsLables } from '../utils';
import './History.less';

const HistoryList = ({ editUser }) => {
  const getTranslationFor = useContext(TranslationsContext);
  const {
    data,
    portalUrl,
    fetchApi,
    loading,
    handleApiResponse,
    setB_size,
    handlePageChange,
    b_size,
    setSorting,
  } = useContext(ApiContext);

  const labels = getHistoryFieldsLables(getTranslationFor);
  const [filters, setFilters] = useState({});
  const [textTimeout, setTextTimeout] = useState(0);
  const [resetPaginationToggle, setResetPaginationToggle] = useState(false);
  const [selectedRows, setSelectedRows] = React.useState([]);

  //------------------COLUMNS----------------------
  const StatusCell = (row, index, column, id) => {
    let statusIcon = '';
    switch (row.status) {
      case 'success':
        statusIcon = (
          <span className="glyphicon glyphicon-ok-sign success"></span>
        );
        break;
      case 'error':
        statusIcon = <span className="glyphicon glyphicon-alert error"></span>;
        break;
      case 'sending':
        statusIcon = <span className="glyphicon glyphicon-hourglass"></span>;
        break;
      default:
        statusIcon = <span>{row.status}</span>;
        break;
    }
    return <div className="status">{statusIcon}</div>;
  };

  const columns = [
    {
      name: labels.status,
      selector: 'status',
      sortable: true,
      cell: StatusCell,
      width: '70px',
    },
    { name: labels.type, selector: 'type', sortable: true, width: '200px' },
    { name: labels.subject, selector: 'subject', sortable: true },
    {
      name: labels.recipients,
      selector: 'recipients',
      sortable: false,
      width: '100px',
    },
    {
      name: labels.date,
      selector: 'date',
      sortable: true,
      cell: row => (
        <div>{format(new Date(row.date), 'dd/MM/yyyy HH:mm:ss')}</div>
      ),
      width: '180px',
    },
    {
      name: labels.completed_date,
      selector: 'completed_date',
      sortable: true,
      cell: row => (
        <div>{format(new Date(row.completed_date), 'dd/MM/yyyy HH:mm:ss')}</div>
      ),
      width: '180px',
    },
  ];

  //------------FILTERING-----------

  const SubHeaderComponent = React.useMemo(() => {
    const handleClearText = () => {
      setResetPaginationToggle(!resetPaginationToggle);
      setFilters({ ...filters, subject: '' });
    };

    const delayTextSubmit = value => {
      const newFilters = { ...filters, subject: value };
      if (textTimeout) {
        clearInterval(textTimeout);
      }
      const timeout = setTimeout(() => {
        doQuery(newFilters);
      }, 1000);
      setFilters(newFilters);
      setTextTimeout(timeout);
    };

    const doQuery = queryFilters => {
      const params = { ...queryFilters };
      if (params.subject?.length) {
        params.subject = params.subject + '*';
      }
      fetchApi(null, params);
    };
    return (
      <>
        <div className="search-wrapper">
          <Select
            isMulti={false}
            isClearable={true}
            inputId="type"
            name={'type'}
            options={[
              { value: 'Comunicato Stampa', label: 'Comunicato Stampa' },
              { value: 'Invito Stampa', label: 'Invito Stampa' },
            ]}
            onChange={options => {
              const newFilters = {
                ...filters,
                type: options ? options.value : null,
              };
              setFilters(newFilters);
              doQuery(newFilters);
            }}
            className="type-select"
            placeholder={getTranslationFor('Select a type', 'Select a type')}
          />
          <input
            id="search"
            type="text"
            placeholder={getTranslationFor('Filter history', 'Filter history')}
            aria-label={getTranslationFor('Search...', 'Search...')}
            value={filters.subject || ''}
            onChange={e => delayTextSubmit(e.target.value)}
          />
          <button type="button" onClick={handleClearText}>
            X
          </button>
        </div>
      </>
    );
  }, [filters, resetPaginationToggle, data.items]);

  return (
    <div className="ufficio-stampa-history-list">
      <DataTable
        columns={columns}
        data={data.items}
        striped={true}
        highlightOnHover={true}
        pointerOnHover={false}
        noDataComponent={getTranslationFor(
          'No send history found',
          'No send history found',
        )}
        responsive={true}
        defaultSortField={DEFAULT_SORT_ON}
        defaultSortAsc={DEFAULT_SORT_ORDER == 'ascending'}
        pagination={true}
        paginationRowsPerPageOptions={[5, 25, 50, 100]}
        paginationPerPage={b_size}
        paginationServer={true}
        paginationServerOptions={{
          persistSelectedOnPageChange: true,
          persistSelectedOnSort: false,
        }}
        paginationTotalRows={data.items_total}
        onChangeRowsPerPage={size => setB_size(size)}
        onChangePage={handlePageChange}
        progressPending={loading}
        sortServer={true}
        onSort={(column, direction) => setSorting(column.selector, direction)}
        paginationResetDefaultPage={resetPaginationToggle} // optionally, a hook to reset pagination to page 1
        subHeader
        subHeaderComponent={SubHeaderComponent}
      />
    </div>
  );
};
export default HistoryList;
