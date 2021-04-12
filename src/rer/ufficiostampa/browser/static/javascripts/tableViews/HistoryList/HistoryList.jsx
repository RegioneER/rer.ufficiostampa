import React, { useState, useEffect, useContext } from 'react';
import DataTable from 'react-data-table-component';

import { TranslationsContext } from '../../TranslationsContext';
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
  const [filterText, setFilterText] = useState('');
  const [resetPaginationToggle, setResetPaginationToggle] = useState(false);
  const [selectedRows, setSelectedRows] = React.useState([]);

  //------------------COLUMNS----------------------
  const ChannelsCellView = (row, index, column, id) => {
    return (
      <div className="channels">
        {row.channels?.map((channel, index) => {
          return (
            <span key={index}>
              {channel}
              {index < row.channels.length - 1 ? ',' : ''}{' '}
            </span>
          );
        })}
      </div>
    );
  };

  const columns = [
    { name: labels.subject, selector: 'subject', sortable: true },
    { name: labels.recipients, selector: 'recipients', sortable: false },
    { name: labels.date, selector: 'date', sortable: true },
    { name: labels.completed_date, selector: 'completed_date', sortable: true },
    { name: labels.status, selector: 'status', sortable: true },
    // {
    //   name: labels.channels,
    //   selector: 'channels',
    //   sortable: true,
    //   cell: ChannelsCellView,
    // },
  ];

  //------------FILTERING-----------

  const SubHeaderComponent = React.useMemo(() => {
    const handleClear = () => {
      if (filterText) {
        setResetPaginationToggle(!resetPaginationToggle);
        setFilterText('');
      }
    };

    return data?.items?.length > 0 ? (
      <>
        <div className="search-wrapper">
          <input
            id="search"
            type="text"
            placeholder={getTranslationFor('Filter history', 'Filter history')}
            aria-label={getTranslationFor('Search...', 'Search...')}
            value={filterText}
            onChange={e => setFilterText(e.target.value)}
          />
          <button type="button" onClick={handleClear}>
            X
          </button>
        </div>
      </>
    ) : null;
  }, [filterText, resetPaginationToggle, data.items]);

  React.useEffect(() => {
    if (filterText?.length > 0) {
      fetchApi(null, [
        {
          i: 'SearchableText',
          o: 'plone.app.querystring.operation.string.contains',
          v: filterText + '*',
        },
      ]);
    } else {
      fetchApi();
    }
  }, [filterText]);

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
