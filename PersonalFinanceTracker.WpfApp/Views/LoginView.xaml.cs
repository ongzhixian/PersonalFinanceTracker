using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

using PersonalFinanceTracker.WpfApp.Services;

namespace PersonalFinanceTracker.WpfApp.Views
{
    /// <summary>
    /// Interaction logic for LoginView.xaml
    /// </summary>
    public partial class LoginView : BaseViewUserControl
    {
        private IAuthenticationService authenticationService;

        public LoginView(IAuthenticationService authenticationService)
        {
            InitializeComponent();
            this.authenticationService = authenticationService;
        }

        private async void Login(object sender, RoutedEventArgs e)
        {
            InstructionText.Text = "Logging in...";
            await authenticationService.AuthenticateCredentialsAsync(UsernameTextBox.Text, UserPasswordBox.Password);
            if (authenticationService.IsUserAuthenticated)
            {
                InstructionText.Text = "Logged in...transferring";
                //base.RaiseApplicationStateChangedEvent();
            }
            else
            {
                InstructionText.Text = "Logged in failed.";
            }
        }


    }
}
