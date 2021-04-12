import React, { useContext } from 'react';
import { TranslationsContext } from '../../TranslationsContext';

import './Modal.less';
const ModalContext = React.createContext();

const ModalBody = ({ children }) => {
  return (
    <ModalContext.Consumer>
      {() => <div className="plone-modal-body">{children}</div>}
    </ModalContext.Consumer>
  );
};
const ModalFooter = ({ children }) => {
  return (
    <ModalContext.Consumer>
      {() => <div className="plone-modal-footer">{children}</div>}
    </ModalContext.Consumer>
  );
};
const Modal = props => {
  const { show, close, children } = props;
  const getTranslationFor = useContext(TranslationsContext);

  return show ? (
    <div className="plone-modal-wrapper">
      <div className={`plone-modal ${show ? 'fade in' : ''}`}>
        <div className="plone-modal-dialog">
          <div className="plone-modal-content">
            <ModalContext.Provider {...props}>
              <div className="plone-modal-header">
                <a
                  className="plone-modal-close"
                  onClick={() => {
                    close();
                  }}
                >
                  ×
                </a>
              </div>
              {children}
            </ModalContext.Provider>
          </div>
        </div>
      </div>
    </div>
  ) : null;
};

Modal.Body = ModalBody;
Modal.Footer = ModalFooter;

export default Modal;
