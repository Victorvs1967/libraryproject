from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime

from .forms import RenewBookModelForm
from .models import Book, Author, BookInstance, Genre, Language

# Create your views here.
def index(request):
    """

    """
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.all().count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    return render(request, 'index.html', context=context)


@permission_required(perm='catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    :param request:
    :param pk:
    :return:
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)

        if form.is_valid():
            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.save()

            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date, })

    content = {'form': form, 'bookinst': book_inst}

    return render(request, 'catalog/book_renew_librarian.html', content)


class BookListView(ListView):
    """

    """
    model = Book
    paginate_by = 20

class BookDetailView(LoginRequiredMixin, DetailView):
    """

    """
    model = Book

class AuthorListView(ListView):
    """

    """
    model = Author
    template_name = 'catalog/author_list.html'
    paginate_by = 20

class AuthorDetailView(LoginRequiredMixin, DetailView):
    """

    """
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """

    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, ListView):
    """

    """
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class AuthorCreate(PermissionRequiredMixin, CreateView):
    """

    """
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '12/10/2016',}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    """

    """
    permission_required = 'catalog.can_mark_returned'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    """

    """
    permission_required = 'catalog.can_mark_returned'
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    """

    """
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = '__all__'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    """

    """
    permission_required = 'catalog.can_mark_returned'
    model = Book
    fields = ['title', 'author', 'summary', 'language']


class BookrDelete(PermissionRequiredMixin, DeleteView):
    """

    """
    permission_required = 'catalog.can_mark_returned'
    model = Book
    success_url = reverse_lazy('books')

