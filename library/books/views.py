from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Comment
from .forms import BookForm, CommentForm

class BookListView(ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(book=self.object)
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
        return context


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    login_url = 'login'


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'book_confirm_delete.html'
    success_url = reverse_lazy('book_list')
    login_url = 'login'

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment_form.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.book_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('book_detail')

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})

@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form, 'book': book})

class CommentCreateView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'comment_form.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['comment_form'] = CommentForm(self.request.POST)
        else:
            data['comment_form'] = CommentForm()
        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_context_data()['comment_form']
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = self.object
            comment.author = self.request.user
            comment.save()
            return redirect('book_detail', pk=self.object.pk)
        else:
            return self.render_to_response(self.get_context_data(form=form))

@login_required
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    book = comment.book
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'comment_form.html', {'form': form, 'book': book})
