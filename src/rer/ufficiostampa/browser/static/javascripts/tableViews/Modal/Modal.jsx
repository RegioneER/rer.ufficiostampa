import React, { useContext, useEffect, createRef } from 'react';
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
  const { show, close, children, className, id, title } = props;
  const getTranslationFor = useContext(TranslationsContext);
  const modalRef = createRef();

  const handleTabKey = e => {
    const focusableModalElements = modalRef.current.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select',
    );
    const firstElement = focusableModalElements[0];
    const lastElement =
      focusableModalElements[focusableModalElements.length - 1];
    const activeElement = document.activeElement;
    let activeElementIsInModal = false;
    focusableModalElements.forEach(e => {
      if (e === activeElement) {
        activeElementIsInModal = true;
      }
    });
    if (
      !e.shiftKey &&
      (activeElement == lastElement || !activeElementIsInModal)
    ) {
      firstElement.focus();
      return e.preventDefault();
    }

    if (
      e.shiftKey &&
      (activeElement == firstElement || !ctiveElementIsInModal)
    ) {
      lastElement.focus();
      e.preventDefault();
    }
  };

  useEffect(() => {
    if (show) {
      const keyListenersMap = new Map([
        [27, close],
        [9, handleTabKey],
      ]);
      function keyListener(e) {
        // get the listener corresponding to the pressed key
        const listener = keyListenersMap.get(e.keyCode);
        // call the listener if it exists
        return listener && listener(e);
      }

      document.addEventListener('keydown', keyListener);

      return () => document.removeEventListener('keydown', keyListener);
    }
  }, [show]);

  return show ? (
    <div
      className={`plone-modal-ufficio-stampa plone-modal-wrapper ${className ??
        ''}`}
    >
      <div className={`plone-modal ${show ? 'fade in' : ''}`}>
        <div
          className="plone-modal-dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby={`${id}_label`}
        >
          <div className="plone-modal-content" ref={modalRef}>
            <ModalContext.Provider {...props}>
              <div className="plone-modal-header">
                {title && <h2 id={id + '_label'}>{title}</h2>}
                <button
                  className="plone-modal-close"
                  onClick={() => {
                    close();
                  }}
                  title={getTranslationFor('Close modal', 'Chiudi')}
                >
                  ×
                </button>
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
