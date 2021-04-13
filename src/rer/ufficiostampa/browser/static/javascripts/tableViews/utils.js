export const getUserFieldsLables = getTranslationFor => {
  return {
    name: getTranslationFor('Name', 'Name'),
    surname: getTranslationFor('Surname', 'Surname'),
    email: getTranslationFor('email', 'E-mail'),
    phone: getTranslationFor('phone', 'Phone'),
    newspaper: getTranslationFor('newspaper', 'Newspaper name'),
    channels: getTranslationFor('channels', 'Channels'),
  };
};

export const getHistoryFieldsLables = getTranslationFor => {
  return {
    subject: getTranslationFor('Subject', 'Subject'),
    recipients: getTranslationFor('Recipients', 'Recipients'),
    date: getTranslationFor('Date', 'Date'),
    completed_date: getTranslationFor('Completed Date', 'Completed Date'),
    status: getTranslationFor('Status', 'Status'),
  };
};