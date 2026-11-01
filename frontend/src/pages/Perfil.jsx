import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router';
import {
  getUserProfile,
  updateUserInfo,
  uploadUserAvatar,
} from '../services/authApi';
import { clearSession, updateSessionProfile, useAuth } from '../services/authSession';
import { User as UserIcon, Download, Shield, History, AlertCircle, ListFilter, LockKeyhole } from 'lucide-react';
import { AccountDeletionRequest } from '../components/AccountDeletionRequest';

export function Perfil() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [fields, setFields] = useState(() => ({
    name: user?.name ?? '', surname: user?.surname ?? '',
    date_of_birth: user?.date_of_birth ?? '',
  }));
  const [saving, setSaving] = useState(false);
  const [editingProfile, setEditingProfile] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [avatarModalOpen, setAvatarModalOpen] = useState(false);
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState('');
  const [avatarSaving, setAvatarSaving] = useState(false);
  const [avatarError, setAvatarError] = useState('');
  const [failedAvatarUrl, setFailedAvatarUrl] = useState('');
  const [sharingStatus, setSharingStatus] = useState('');
  const avatarInputRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated) return undefined;
    let active = true;
    getUserProfile()
      .then((profile) => {
        if (!active) return;
        updateSessionProfile(profile);
        setFields({
          name: profile.name,
          surname: profile.surname,
          date_of_birth: profile.date_of_birth ?? '',
        });
      })
      .catch((err) => {
        if (!active) return;
        if (err.status === 401) {
          clearSession();
          navigate('/', { state: { mensagem: 'Sua sessão expirou. Entre novamente.' } });
        }
      });
    return () => { active = false; };
  }, [isAuthenticated, navigate]);

  useEffect(() => () => {
    if (avatarPreview) URL.revokeObjectURL(avatarPreview);
  }, [avatarPreview]);

  const closeAvatarModal = () => {
    if (avatarSaving) return;
    setAvatarModalOpen(false);
    setAvatarFile(null);
    setAvatarPreview('');
    setAvatarError('');
  };

  const handleAvatarFile = (event) => {
    const file = event.target.files?.[0] ?? null;
    event.target.value = '';
    if (!file || avatarSaving) return;
    setAvatarError('');
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleAvatarUpload = async () => {
    if (!avatarFile || avatarSaving) return;
    setAvatarSaving(true);
    setAvatarError('');
    try {
      const profile = await uploadUserAvatar(avatarFile);
      updateSessionProfile(profile);
      setFailedAvatarUrl('');
      setMessage('Foto de perfil atualizada com sucesso.');
      setAvatarModalOpen(false);
      setAvatarFile(null);
      setAvatarPreview('');
    } catch (err) {
      if (err.status === 401) {
        clearSession();
        navigate('/', { state: { mensagem: 'Sua sessão expirou. Entre novamente.' } });
        return;
      }
      setAvatarError(err.message || 'Não foi possível atualizar a foto.');
    } finally {
      setAvatarSaving(false);
    }
  };

  const handleSave = async (event) => {
    event.preventDefault();
    if (saving) return;
    setError('');
    setMessage('');
    const changes = Object.fromEntries(Object.entries(fields)
      .map(([key, value]) => [key, value.trim()])
      .filter(([key, value]) => value !== (user?.[key] ?? '')));
    if (!Object.keys(changes).length) {
      setMessage('Nenhuma alteração para salvar.');
      return;
    }
    if (Object.values(changes).some((value) => !value)) {
      setError('Os campos alterados não podem ficar vazios.');
      return;
    }
    if (changes.date_of_birth && changes.date_of_birth >= `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}-${String(new Date().getDate()).padStart(2, '0')}`) {
      setError('A data de nascimento deve estar no passado.');
      return;
    }
    setSaving(true);
    try {
      const profile = await updateUserInfo(changes);
      updateSessionProfile(profile);
      setFields({ name: profile.name, surname: profile.surname,
        date_of_birth: profile.date_of_birth ?? '' });
      setEditingProfile(false);
      setMessage('Perfil atualizado com sucesso.');
    } catch (err) {
      if (err.status === 401) {
        clearSession();
        navigate('/', { state: { mensagem: 'Sua sessão expirou. Entre novamente.' } });
        return;
      }
      setError(err.message || 'Não foi possível atualizar o perfil.');
    } finally {
      setSaving(false);
    }
  };

  const startProfileEditing = () => {
    setFields({
      name: user?.name ?? '',
      surname: user?.surname ?? '',
      date_of_birth: user?.date_of_birth ?? '',
    });
    setError('');
    setMessage('');
    setEditingProfile(true);
  };

  const cancelProfileEditing = () => {
    setFields({
      name: user?.name ?? '',
      surname: user?.surname ?? '',
      date_of_birth: user?.date_of_birth ?? '',
    });
    setError('');
    setMessage('');
    setEditingProfile(false);
  };

  const hasProfileChanges = Object.entries(fields).some(
    ([key, value]) => value.trim() !== String(user?.[key] ?? ''),
  );

  const compartilhamentos = [
    { id: '1', profissional: 'Dra. Maria Silva', data: '5 de Maio, 2026', status: 'Ativo' },
    { id: '2', profissional: 'Dr. João Santos', data: '20 de Abril, 2026', status: 'Ativo' },
    { id: '3', profissional: 'Dra. Ana Costa', data: '10 de Março, 2026', status: 'Expirado' },
  ];
  const filteredCompartilhamentos = sharingStatus
    ? compartilhamentos.filter((compartilhamento) => compartilhamento.status === sharingStatus)
    : compartilhamentos;

  const handleExportarDados = () => {
    alert('A exportação de dados ainda não está disponível.');
  };

  return (
    <div className="profile-page admin-fixed-shell min-h-screen bg-background p-5 md:p-8">
      <div className="admin-fixed-page max-w-5xl mx-auto">
        <header className="catalog-page-header catalog-page-intro profile-page-header">
          <div className="catalog-page-intro-copy">
            <h1 className="text-3xl">Perfil e privacidade</h1>
            <p>Gerencie suas informações pessoais e configurações de privacidade.</p>
          </div>
        </header>

        <div className="admin-scroll-region">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-card rounded-2xl border border-border p-6">
              <div className="profile-card-heading">
                <h2 className="text-xl font-semibold">Informações pessoais</h2>
                {isAuthenticated && !editingProfile && <button type="button" className="catalog-button catalog-hover-secondary" onClick={startProfileEditing}>Editar informações</button>}
              </div>

              <div className="flex flex-col items-center justify-center mb-6 gap-3">
                <div className="w-24 h-24 mx-auto bg-primary/10 rounded-full flex items-center justify-center overflow-hidden border border-border">
                  {user?.avatar_url && user.avatar_url !== failedAvatarUrl ? (
                    <img
                      src={user.avatar_url}
                      alt="Foto de perfil"
                      className="w-full h-full object-cover object-center"
                      onError={() => setFailedAvatarUrl(user.avatar_url)}
                    />
                  ) : (
                    <UserIcon className="w-12 h-12 text-primary" />
                  )}
                </div>
                {isAuthenticated && (
                  <button
                    type="button"
                    onClick={() => {
                      setAvatarModalOpen(true);
                      setAvatarError('');
                    }}
                    className="text-sm px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    {user?.avatar_url ? 'Alterar foto' : 'Adicionar foto'}
                  </button>
                )}
              </div>

              {!isAuthenticated ? (
                <p role="alert">Entre na sua conta para editar o perfil. <Link to="/" className="text-primary">Ir para login</Link></p>
              ) : (
                <form onSubmit={handleSave} className="space-y-4">
                  <fieldset disabled={saving} className="space-y-4">
                    <div className="profile-fields-grid">
                    {[
                      ['name', 'Nome', 'text'], ['surname', 'Sobrenome', 'text'],
                      ['date_of_birth', 'Data de nascimento', 'date'],
                    ].map(([key, label, type]) => (
                      <div className="profile-field" key={key}>
                        <label htmlFor={key} className="block mb-2">{label}</label>
                        <input id={key} type={type} value={fields[key]}
                          maxLength={type === 'text' ? 200 : undefined}
                          required={key === 'name' || key === 'surname'}
                          readOnly={!editingProfile}
                          aria-readonly={!editingProfile}
                          onChange={(event) => {
                            setFields({ ...fields, [key]: event.target.value });
                            setMessage('');
                            setError('');
                          }}
                          className={`w-full px-4 py-3 rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring ${editingProfile ? 'bg-input-background' : 'profile-readonly-input'}`} />
                      </div>
                    ))}
                    </div>
                    <div>
                      <label htmlFor="email" className="block mb-2">E-mail</label>
                      <input id="email" type="email" value={user?.email ?? ''} readOnly
                        className="profile-readonly-input w-full px-4 py-3 rounded-lg border border-border" />
                      <p className="mt-1 text-sm text-muted-foreground">A alteração de e-mail ainda não está disponível.</p>
                    </div>
                    {editingProfile && <div className="profile-form-actions">
                        <div className="profile-edit-actions">
                          <button type="button" className="catalog-button" onClick={cancelProfileEditing}>Cancelar</button>
                          <button type="submit" className="catalog-primary" disabled={saving || !hasProfileChanges}>{saving ? 'Salvando...' : 'Salvar alterações'}</button>
                        </div>
                    </div>}
                  </fieldset>
                  {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
                  {message && <p role="status" className="text-sm text-primary">{message}</p>}
                </form>
              )}
            </div>

            <div className="bg-card rounded-2xl border border-border p-6">
              <div className="profile-section-heading">
                <h2 className="text-xl font-semibold">Histórico de compartilhamentos</h2>
                <div className="profile-sharing-filter">
                  <button type="button" className="catalog-button profile-sharing-filter-trigger" aria-haspopup="true">
                    <ListFilter size={15} aria-hidden="true" />Filtrar
                    {sharingStatus && <span aria-label={`Filtro ativo: ${sharingStatus}`} />}
                  </button>
                  <div className="profile-sharing-filter-popover">
                    <label htmlFor="sharing-status">Status</label>
                    <select id="sharing-status" value={sharingStatus} onChange={(event) => setSharingStatus(event.target.value)}>
                      <option value="">Todos</option>
                      <option value="Ativo">Ativos</option>
                      <option value="Inativo">Inativos</option>
                      <option value="Expirado">Expirados</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                {filteredCompartilhamentos.map((comp) => (
                  <div key={comp.id} className="flex items-center justify-between p-4 bg-muted rounded-xl">
                    <div>
                      <div className="mb-1">{comp.profissional}</div>
                      <div className="text-sm text-muted-foreground">{comp.data}</div>
                    </div>
                    <span className={`sharing-status sharing-status-${comp.status.toLowerCase()}`}>
                      {comp.status}
                    </span>
                  </div>
                ))}
                {!filteredCompartilhamentos.length && <p className="profile-sharing-empty">Nenhum compartilhamento encontrado para este status.</p>}
              </div>
            </div>

          </div>

          <div className="lg:col-span-1 space-y-6">
            <div className="bg-card rounded-2xl border border-border p-6">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="w-5 h-5 text-primary" />
                <h3>Preferências de privacidade</h3>
              </div>

              <div className="space-y-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm">Permitir análise por IA</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary" />
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm">Receber recomendações</span>
                  <input type="checkbox" defaultChecked className="w-5 h-5 accent-primary" />
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm">Notificações por e-mail</span>
                  <input type="checkbox" className="w-5 h-5 accent-primary" />
                </label>
              </div>
            </div>

            <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl border border-border p-6">
              <div className="flex items-center gap-3 mb-3">
                <History className="w-5 h-5 text-primary" />
                <h3>Estatísticas</h3>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Reflexões registradas</span>
                  <span>47</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Dias consecutivos</span>
                  <span>12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Temas explorados</span>
                  <span>15</span>
                </div>
              </div>
            </div>

            <div className="profile-privacy-card bg-card rounded-2xl border border-border">
              <div className="flex items-center gap-3 mb-4">
                <LockKeyhole className="w-5 h-5 text-primary" />
                <h3>Privacidade e dados</h3>
              </div>

              <div className="profile-privacy-actions space-y-3">
                <button
                  onClick={handleExportarDados}
                  className="w-full flex items-center justify-center gap-2 border border-border rounded-lg hover:bg-muted transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Exportar meus dados
                </button>

                <div className="profile-privacy-note flex gap-2.5 bg-muted rounded-lg">
                  <AlertCircle className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                  <p className="text-muted-foreground">
                    Você controla seus dados e pode exportá-los ou solicitar a exclusão da conta.
                  </p>
                </div>

                <AccountDeletionRequest />
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      {avatarModalOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="avatar-modal-title"
        >
          <div className="w-full max-w-md bg-card border border-border rounded-2xl p-6 shadow-xl">
            <h2 id="avatar-modal-title" className="text-xl mb-5 text-center">
              {user?.avatar_url ? 'Alterar foto de perfil' : 'Adicionar foto de perfil'}
            </h2>

            <div className="flex justify-center mb-3">
              <div className="w-32 h-32 rounded-full bg-primary/10 border border-border overflow-hidden flex items-center justify-center">
                {avatarPreview || (user?.avatar_url && user.avatar_url !== failedAvatarUrl) ? (
                  <img
                    src={avatarPreview || user.avatar_url}
                    alt="Prévia centralizada da foto de perfil"
                    className="w-full h-full object-cover object-center"
                  />
                ) : (
                  <UserIcon className="w-14 h-14 text-primary" />
                )}
              </div>
            </div>

            <input
              ref={avatarInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
              onChange={handleAvatarFile}
              disabled={avatarSaving}
              className="sr-only"
              tabIndex={-1}
              aria-hidden="true"
            />

            <div className="flex justify-center mb-5">
              <button
                type="button"
                onClick={() => avatarInputRef.current?.click()}
                disabled={avatarSaving}
                className="px-4 py-2 rounded-lg border border-border hover:bg-muted disabled:opacity-60"
              >
                Escolher arquivo
              </button>
            </div>

            {avatarError && <p role="alert" className="mb-4 text-center text-sm text-destructive">{avatarError}</p>}

            <div className="flex flex-wrap justify-start gap-3">
              <button
                type="button"
                onClick={closeAvatarModal}
                disabled={avatarSaving}
                className="px-4 py-2 rounded-lg border border-border hover:bg-muted disabled:opacity-60"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleAvatarUpload}
                disabled={avatarSaving || !avatarFile}
                className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-60"
              >
                {avatarSaving ? 'Salvando...' : 'Salvar foto'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
