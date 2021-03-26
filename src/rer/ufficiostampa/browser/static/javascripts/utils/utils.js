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
