import React, { useState, useEffect, useContext } from 'react';
import DataTable from 'react-data-table-component';

import { TranslationsContext } from '../TranslationsContext';
import {
  SubscriptionsContext,
  DEFAULT_B_SIZE,
  DEFAULT_SORT_ON,
  DEFAULT_SORT_ORDER,
} from '../SubscriptionsContext';
import apiFetch from '../utils/apiFetch';
import { getUserFieldsLables } from '../utils/utils';
import './Users.less';

const UsersList = ({ editUser }) => {
  const getTranslationFor = useContext(TranslationsContext);
  const {
    subscriptions,
    portalUrl,
    fetchSubscriptions,
    loading,
    handleApiResponse,
    setB_size,
    handlePageChange,
    b_size,
    setSorting,
  } = useContext(SubscriptionsContext);

  const labels = getUserFieldsLables(getTranslationFor);
  const [filterText, setFilterText] = useState('');
  const [resetPaginationToggle, setResetPaginationToggle] = useState(false);
  const [toggleCleared, setToggleCleared] = useState(false);
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
    { name: labels.name, selector: 'name', sortable: true },
    { name: labels.surname, selector: 'surname', sortable: true },
    { name: labels.email, selector: 'email', sortable: true },
    { name: labels.phone, selector: 'phone', sortable: true },
    { name: labels.newspaper, selector: 'newspaper', sortable: true },
    {
      name: labels.channels,
      selector: 'channels',
      sortable: true,
      cell: ChannelsCellView,
    },
    {
      name: getTranslationFor('Actions', 'Actions'),
      button: true,
      cell: row => (
        <button
          className="action editItem plone-btn plone-btn-primary plone-btn-link"
          onClick={() => {
            editUser(row);
          }}
          title={getTranslationFor('Edit', 'Edit')}
        >
          <span className="glyphicon glyphicon-pencil"></span>
        </button>
      ),
    },
  ];

  //------------ROW SELECTION------------
  const handleRowSelected = React.useCallback(state => {
    setSelectedRows(state.selectedRows);
  }, []);

  const contextActions = React.useMemo(() => {
    const handleDelete = () => {
      // eslint-disable-next-line no-alert
      if (
        window.confirm(
          `${getTranslationFor(
            'Are you sure you want to delete this subscribed users?',
            'Are you sure you want to delete this subscribed users?',
          )} \n${selectedRows
            .map(r => r.name + ' ' + r.surname + ' (' + r.email + ')')
            .join('\n')}`,
        )
      ) {
        setToggleCleared(!toggleCleared);

        //call delete foreach item selected
        let url = portalUrl + '/@subscriptions';
        let method = 'DELETE';
        let fetches = [];

        selectedRows.forEach(r => {
          fetches.push(
            apiFetch({
              url: url + '/' + r.id,
              method: method,
            }),
          );
        });

        Promise.all(fetches).then(data => {
          handleApiResponse(data[0]);
          fetchSubscriptions();
        });
      }
    };

    return (
      <button
        key="delete"
        onClick={handleDelete}
        className="plone-btn plone-btn-danger"
      >
        {getTranslationFor('Delete', 'Delete')}
      </button>
    );
  }, [subscriptions.items, selectedRows, toggleCleared]);

  //------------FILTERING-----------

  const SubHeaderComponent = React.useMemo(() => {
    const handleClear = () => {
      if (filterText) {
        setResetPaginationToggle(!resetPaginationToggle);
        setFilterText('');
      }
    };

    return subscriptions?.items?.length > 0 ? (
      <>
        <div className="search-wrapper">
          <input
            id="search"
            type="text"
            placeholder={getTranslationFor(
              'Filter subscribers',
              'Filter subscribers',
            )}
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
  }, [filterText, resetPaginationToggle, subscriptions.items]);

  React.useEffect(() => {
    if (filterText?.length > 0) {
      fetchSubscriptions(null, [
        {
          i: 'SearchableText',
          o: 'plone.app.querystring.operation.string.contains',
          v: filterText + '*',
        },
      ]);
    } else {
      fetchSubscriptions();
    }
  }, [filterText]);

  return (
    <div className="ufficio-stampa-users-list">
      <DataTable
        title={getTranslationFor('Subscribers', 'Subscribers')}
        columns={columns}
        data={subscriptions.items}
        striped={true}
        highlightOnHover={true}
        pointerOnHover={false}
        noDataComponent={getTranslationFor(
          'No subscribers found',
          'No subscribers found',
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
        paginationTotalRows={subscriptions.items_total}
        onChangeRowsPerPage={size => setB_size(size)}
        onChangePage={handlePageChange}
        progressPending={loading}
        sortServer={true}
        onSort={(column, direction) => setSorting(column.selector, direction)}
        paginationResetDefaultPage={resetPaginationToggle} // optionally, a hook to reset pagination to page 1
        subHeader
        subHeaderComponent={SubHeaderComponent}
        selectableRows
        onSelectedRowsChange={handleRowSelected}
        contextActions={contextActions}
        clearSelectedRows={toggleCleared}
      />
    </div>
  );
};
export default UsersList;
